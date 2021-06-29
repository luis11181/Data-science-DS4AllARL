
#* pip install -r requirements.txt -t libraries 
#! script to connect to db from terminal
# psql -h dbpositiva.cogq7bwdrted.us-east-2.rds.amazonaws.com -U mainuser -p 5432


#! script to connect and query from db to pandas
from sqlalchemy import create_engine #Crea la conexión que se puede usar con pandas
import psycopg2 as pg #Crea conexión para hacer queries en general (incluso operaciones de INSERT)
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import missingno as msno  #libreria para plotear datos faltantes

conn = pg.connect(user = "mainuser", password = "positivaadmin", host = "dbpositiva.cogq7bwdrted.us-east-2.rds.amazonaws.com",  port = "5432", database = "positiva")
                        
engine = create_engine("postgresql://mainuser:positivaadmin@dbpositiva.cogq7bwdrted.us-east-2.rds.amazonaws.com/positiva")

Eretiradas = pd.read_sql_query("SELECT * FROM dempresas_retiradas", engine) # Returns a DataFrame corresponding to the result set of the query string. Optionally provide an index_col parameter to use one of the columns as the index, otherwise default integer index will be used.

Causalretiro = pd.read_sql_query("SELECT * FROM dcausal_retiro", engine)

Eretiradas = pd.read_sql_query("SELECT * FROM dcausal_retiro LIMIT 10000", engine)

print('informacion basica empresas retiradas=')
print(Eretiradas.info())
print('datos unicos=')
print(Eretiradas.nunique())
print('null data:')
print(Eretiradas.isnull().value_counts())

print(r'%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
print('informacion basica causal retiro=')
print(Causalretiro.info())
print('datos unicos=')
print(Causalretiro.nunique())
print('null data:')
print(Causalretiro.isnull().value_counts())