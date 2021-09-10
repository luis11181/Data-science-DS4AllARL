import os
import pickle
from data import eval, desc

seccion_dict = {'SECCIÓN A': 'AGRICULTURA, GANADERÍA, CAZA, SILVICULTURA Y PESCA',
                'SECCIÓN B': 'EXPLOTACIÓN DE MINAS Y CANTERAS',
                'SECCIÓN C': 'INDUSTRIAS MANUFACTURERAS',
                'SECCIÓN D': 'SUMINISTRO DE ELECTRICIDAD, GAS, VAPOR Y AIRE ACONDICIONADO',
                'SECCIÓN E': 'DISTRIBUCIÓN DE AGUA; EVACUACIÓN Y TRATAMIENTO DE AGUAS RESIDUALES, GESTIÓN DE DESECHOS Y ACTIVIDADES DE SANEAMIENTO AMBIENTAL',
                'SECCIÓN F': 'CONSTRUCCIÓN',
                'SECCIÓN G': 'COMERCIO AL POR MAYOR Y AL POR MENOR; REPARACIÓN DE VEHÍCULOS AUTOMOTORES Y MOTOCICLETAS',
                'SECCIÓN H': 'TRANSPORTE Y ALMACENAMIENTO',
                'SECCIÓN I': 'ALOJAMIENTO Y SERVICIOS DE COMIDA',
                'SECCIÓN J': 'INFORMACIÓN Y COMUNICACIONES',
                'SECCIÓN K': 'ACTIVIDADES FINANCIERAS Y DE SEGUROS',
                'SECCIÓN L': 'ACTIVIDADES INMOBILIARIAS',
                'SECCIÓN M': 'ACTIVIDADES PROFESIONALES, CIENTÍFICAS Y TÉCNICAS',
                'SECCIÓN N': 'ACTIVIDADES DE SERVICIOS ADMINISTRATIVOS Y DE APOYO',
                'SECCIÓN O': 'ADMINISTRACIÓN PÚBLICA Y DEFENSA; PLANES DE SEGURIDAD SOCIAL DE AFILIACIÓN OBLIGATORIA',
                'SECCIÓN P': 'EDUCACIÓN',
                'SECCIÓN Q': 'ACTIVIDADES DE ATENCIÓN DE LA SALUD HUMANA Y DE ASISTENCIA SOCIAL',
                'SECCIÓN R': 'ACTIVIDADES ARTÍSTICAS, DE ENTRETENIMIENTO Y RECREACIÓN',
                'SECCIÓN S': 'OTRAS ACTIVIDADES DE SERVICIOS',
                'SECCIÓN T': 'ACTIVIDADES DE LOS HOGARES INDIVIDUALES EN CALIDAD DE EMPLEADORES; ACTIVIDADES NO DIFERENCIADAS DE LOS HOGARES INDIVIDUALES COMO PRODUCTORES DE BIENES Y SERVICIOS PARA USO PROPIO',
                'SECCIÓN U': 'ACTIVIDADES DE ORGANIZACIONES Y ENTIDADES EXTRATERRITORIALES'}

model_dict = {'LR': 0, 'KNN': 1, 'CART': 2, 'RF': 3, 'SVM': 4, 'MLP': 5}


def model_predict_proba(model_key='LR'):
    script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
    rel_path = "models.pkl"
    abs_file_path = os.path.join(script_dir, rel_path)
    m = model_dict[model_key]
    models = pickle.load(open(abs_file_path, 'rb'))

    prob = models[m]['model'].predict_proba(eval)[:, 1]
    desc['prob'] = prob
    desc['seccion'] = desc['seccion'].replace(seccion_dict)

    ans = desc.sort_values(by='prob', ascending=False)

    return ans
