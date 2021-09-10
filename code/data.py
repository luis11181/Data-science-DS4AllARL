import pickle
import pandas as pd
import os

from sqlalchemy import create_engine

#####################################################################################
# Connect to database and load que data for all queryes
conn = create_engine(
    'postgresql://database')

# Get database
query = '''
SELECT * FROM public."queryGraficasDescriptivas"
;
'''


df = pd.read_sql_query(query, conn  # ,
                       #dtype = {'actividad_economica':np.int32,                            'relaciones_laborales':np.int32,'anio':np.int16, 'mes':np.int8}
                       )

# chnge some column types, add year and yearmonth for the graphs
df.corte = pd.to_datetime(df['corte'])
df['year'] = pd.DatetimeIndex(df['corte']).year
df['yearmonth'] = (pd.DatetimeIndex(df['corte']).year.astype(
    str)+pd.DatetimeIndex(df['corte']).month.astype(str)).astype(int)


# Get causal de retiro db
cr_query = '''
SELECT anio, detalle_causa FROM dcausal_retiro;
'''

cr = pd.read_sql_query(cr_query, conn)

# Get voz del cliente

vx_query = '''
SELECT numero, fecha_radicacion, causa_traslado, detalle_causa, descripcion_traslado FROM dcausal_retiro
ORDER BY fecha_radicacion DESC;
'''

vx = pd.read_sql_query(vx_query, conn)

# Get models data
query = '''
SELECT * FROM model_query WHERE ultimo_corte = (SELECT MAX(ultimo_corte) FROM model_query);
'''

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

categorical = pd.get_dummies(df_models[['seccion', 'tamano_emp', 'suc_sucursal',
                                        'departamento', 'mes_retiro']],
                             columns=['seccion', 'tamano_emp', 'suc_sucursal', 'departamento', 'mes_retiro'])
reals = df_models.drop(
    ['seccion', 'tamano_emp', 'suc_sucursal', 'departamento', 'municipio',
     'mes_retiro', 'ultimo_corte', 'segmento', 'retiro'], axis=1)

script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
rel_path = "forecast/scaler.pkl"
abs_file_path = os.path.join(script_dir, rel_path)

scaler = pickle.load(open(abs_file_path, 'rb'))

eval = pd.concat([pd.DataFrame(scaler.transform(reals), columns=reals.columns,
                               index=reals.index), categorical], axis=1)
desc = df_models.reset_index()[['numero', 'seccion', 'departamento',
                               'municipio', 'segmento', 'tamano_emp']]
