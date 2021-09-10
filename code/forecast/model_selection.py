import pickle
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime as dt
from sqlalchemy import create_engine

from sklearn.preprocessing import StandardScaler

from sklearn.metrics import confusion_matrix, precision_recall_curve, average_precision_score

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier


def max_f_measure(y_true, y_scores):
    precision, recall, thresholds = precision_recall_curve(y_true, y_scores)
    f_measures = (2 * (precision * recall) / (precision + recall + 1e-5))
    return {'f1_score': f_measures.max(), 'threshold': thresholds[f_measures.argmax()]}


# setup plot details
def plot_pr_curves(mod_res):
    colors = sns.color_palette("husl", len(mod_res))

    plt.figure(figsize=(8, 7))
    f_scores = np.linspace(0.2, 0.8, num=4)
    lines = []
    labels = []
    for f_score in f_scores:
        x = np.linspace(0.01, 1)
        y = f_score * x / (2 * x - f_score)
        l, = plt.plot(x[y >= 0], y[y >= 0], color='gray', alpha=0.2)
        plt.annotate('f1={0:0.1f}'.format(f_score), xy=(0.9, y[45] + 0.02))

    lines.append(l)
    labels.append('iso-f1 curves')

    for i, m in enumerate(mod_res):
        l, = plt.plot(m['metrics']['recall'],
                      m['metrics']['precision'], color=colors[i], lw=2)
        lines.append(l)
        labels.append(f"{m['name']} (AP: {m['metrics']['ap']:0.2f})")

    fig = plt.gcf()
    fig.subplots_adjust(right=0.75)
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.title('Model comparison - Precision-Recall curve')
    #plt.legend(lines, labels, loc=(0, -.38), prop=dict(size=14))
    plt.legend(lines, labels, bbox_to_anchor=(1.05, 1),
               loc='upper left', borderaxespad=0.)
    plt.savefig('pr_curves.png')


def plot_cm(y_true, y_scores, threshold=0.5, normalize=None):
    plt.figure()
    y_pred = (y_scores > threshold).astype(int)
    cm = confusion_matrix(y_true, y_pred)
    if normalize is None:
        pass
    elif normalize == 'true':
        cm = (cm.T/np.sum(cm, 1)).T
    elif normalize == 'pred':
        cm = cm/np.sum(cm, 0)
    elif normalize == 'all':
        cm = cm/np.sum(cm)
    else:
        raise NotImplemented

    sns.heatmap(cm, annot=True,
                fmt='.2%', cmap='Blues')
    plt.title(f'Confusion matrix (Threshold: {threshold:.2f})')
    plt.xlabel('Predicted label')
    plt.ylabel('True label')


seed = 123

conn = create_engine(
    'postgresql://mainuser:positivaadmin@dbpositiva.cogq7bwdrted.us-east-2.rds.amazonaws.com:5432/positiva')


def preprocess_data(query, conn):
    df_models = pd.read_sql_query(query, conn).set_index('numero')
    df_models = df_models.replace({'seccion': {'SECCIÓN H ': 'SECCIÓN H'},
                                   'suc_sucursal': {'GUAJIRA': 'LA GUAJIRA', 'URABA': 'ANTIOQUIA',
                                                    'Calidad de Datos': 'Sin Datos'}})
    secciones = ['SECCIÓN A', 'SECCIÓN B', 'SECCIÓN C', 'SECCIÓN D', 'SECCIÓN E', 'SECCIÓN F', 'SECCIÓN G', 'SECCIÓN H',
                 'SECCIÓN I', 'SECCIÓN J', 'SECCIÓN K', 'SECCIÓN L', 'SECCIÓN M', 'SECCIÓN N', 'SECCIÓN O', 'SECCIÓN P', 'SECCIÓN Q']
    tamanos = ['Pequeña', 'Mediana', 'Grande']
    sucursales = ['Sin Datos', 'AMAZONAS', 'ANTIOQUIA', 'ARAUCA', 'ATLANTICO', 'BOGOTA D.C.', 'BOLIVAR', 'BOYACA', 'CALDAS', 'CAQUETA', 'CASANARE', 'CAUCA', 'CESAR', 'CHOCO', 'CORDOBA', 'CUNDINAMARCA', 'HUILA', 'LA GUAJIRA', 'MAGDALENA',
                  'META', 'NARINO', 'NARIÑO', 'NORTE DE SANTANDER', 'PUTUMAYO', 'QUINDIO', 'RISARALDA', 'SAN ANDRES', 'SAN ANDRES Y PROV', 'SANTANDER', 'SUCRE', 'TOLIMA', 'VALLE', 'VALLE DEL CAUCA']
    departamentos = ['AMAZONAS', 'ANTIOQUIA', 'ARAUCA', 'ATLANTICO', 'BOGOTA D.C.', 'BOLIVAR', 'BOYACA', 'CALDAS', 'CAQUETA', 'CASANARE', 'CAUCA', 'CESAR', 'CHOCO', 'CORDOBA', 'CUNDINAMARCA', 'GUANIA', 'GUAVIARE', 'HUILA',
                     'LA GUAJIRA', 'MAGDALENA', 'META', 'NARIÑO', 'NORTE DE SANTANDER', 'PUTUMAYO', 'QUINDIO', 'RISARALDA', 'SAN ANDRES Y PROV', 'SANTANDER', 'SUCRE', 'TOLIMA', 'VALLE DEL CAUCA', 'VAUPES', 'VICHADA']

    df_models['seccion'] = pd.Categorical(
        df_models['seccion'], categories=secciones)
    df_models['tamano_emp'] = pd.Categorical(
        df_models['tamano_emp'], categories=tamanos)
    df_models['suc_sucursal'] = pd.Categorical(
        df_models['suc_sucursal'], categories=sucursales)
    df_models['departamento'] = pd.Categorical(
        df_models['departamento'], categories=departamentos)
    df_models['mes_retiro'] = pd.Categorical(
        pd.to_datetime(df_models.ultimo_corte).dt.month, categories=range(1, 13))

    retiradas = df_models.loc[df_models.retiro !=
                              0, ['ultimo_corte', 'tamano_emp', 'retiro']]
    retiradas_train = retiradas[retiradas.ultimo_corte <
                                dt.strptime('2020-01-01', '%Y-%m-%d').date()]

    no_retiradas = df_models.loc[df_models.retiro ==
                                 0, ['ultimo_corte', 'tamano_emp', 'retiro']]
    n_train = int(len(no_retiradas)/len(retiradas)*len(retiradas_train))
    no_retiradas_train = no_retiradas.sample(n=n_train, random_state=seed)

    train = pd.concat([retiradas_train, no_retiradas_train])

    y = (df_models.loc[:, 'retiro'] > 0).astype(int)
    categorical = pd.get_dummies(df_models[['seccion', 'tamano_emp', 'suc_sucursal',
                                            'departamento', 'mes_retiro']],
                                 columns=['seccion', 'tamano_emp', 'suc_sucursal', 'departamento', 'mes_retiro'])
    reals = df_models.drop(
        ['seccion', 'tamano_emp', 'suc_sucursal', 'departamento', 'municipio',
         'mes_retiro', 'ultimo_corte', 'segmento', 'retiro'], axis=1)

    scaler = StandardScaler()
    scaler.fit(reals)

    idxs = df_models.index.isin(train.index)

    X_train = pd.concat([pd.DataFrame(scaler.transform(reals[idxs]),
                                      columns=reals.columns), categorical[idxs].reset_index(drop=True)], axis=1)
    y_train = y[idxs]
    X_test = pd.concat([pd.DataFrame(scaler.transform(reals[~idxs]),
                                     columns=reals.columns), categorical[~idxs].reset_index(drop=True)], axis=1)
    y_test = y[~idxs]

    return scaler, X_train, y_train, X_test, y_test


query = '''
SELECT * FROM model_query;
'''

scaler, X_train, y_train, X_test, y_test = preprocess_data(query, conn)
pickle.dump(scaler, open('./scaler.pkl', 'wb'))

models = []
models.append(('LR', LogisticRegression(random_state=seed,
              max_iter=1000, fit_intercept=False, class_weight='balanced')))
models.append(('KNN', KNeighborsClassifier(n_neighbors=5,)))
models.append(('CART', DecisionTreeClassifier(
    random_state=seed, class_weight='balanced')))
models.append(('RF', RandomForestClassifier(
    n_estimators=100, random_state=seed)))
models.append(('SVM', SVC(random_state=seed, class_weight='balanced',
                          probability=True)))
models.append(('MLP', MLPClassifier(
    hidden_layer_sizes=(20, 5), random_state=seed)))


mod_res = []
for name, model in models:
    model.fit(X_train, y_train)
    p_pred = model.predict_proba(X_test)[:, 1]
    precision, recall, _ = precision_recall_curve(y_test, p_pred)
    average_precision = average_precision_score(y_test, p_pred)
    mod_res.append({'name': name, 'model': model,
                    'metrics': {'precision': precision,
                                'recall': recall,
                                'ap': average_precision}})
    plot_cm(y_test, p_pred, 0.5, normalize='true')
    plt.savefig(f'cm_{name}.png')

import os
script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
rel_path = "models.pkl"
abs_file_path = os.path.join(script_dir, rel_path)

pickle.dump(mod_res, open(abs_file_path, 'wb'))

plot_pr_curves(mod_res)
