#### ----------------------------
#### Librerías
#### ----------------------------
import pandas as pd
from ftplib import FTP_TLS
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
import time
import re
import traceback
from pydataxm.pydataxm import ReadDB

## -- Cargar variables de entorno
load_dotenv()
## -- Cargar variables de entorno
load_dotenv()

clave_db=os.getenv('clave_db')
usuario_db=os.getenv('usuario_db')
db=os.getenv('db')
usuario_xm=os.getenv('usuario_xm')
clave_xm=os.getenv('clave_xm')

# #### ----------------------------
# #### Ventanas de tiempo
# #### ----------------------------

hoy = datetime.now().date()
if hoy.day > 5:
    inicio_mes = datetime(hoy.year,hoy.month,1)
    fin_mes =  datetime(hoy.year,hoy.month +1 ,1) - timedelta(1)
else:
    inicio_mes = datetime(hoy.year,hoy.month-1,1)
    fin_mes =  datetime(hoy.year,hoy.month ,1) - timedelta(1)
    
# #### ----------------------------
# #### Funciones
# #### ----------------------------

## -- 1. API simple

for i in range(3):
    try:
            api = ReadDB().request_data
            break
    except:
        time.sleep(5)
        

def apiMejorada(variable="Gene",tipo="Sistema",inicio=inicio_mes,fin=hoy,filtros=False):
    for i in range(3):
        try:
            if filtros:
                datos = api(variable,tipo,inicio,fin,filtros).drop_duplicates()
                break
            else:
                datos = api(variable,tipo, inicio,fin).drop_duplicates()
                break
        except:
            time.sleep(5)
            datos = pd.DataFrame()
    return datos

#### ----------------------------
#### Conexión con PostgreSQL
#### ----------------------------

def conexionDB(db=db,clave=clave_db,usuario=usuario_db,puerto="5432"):
        DB_HOST = "145.223.73.154"; DB_NAME = db; DB_USER = usuario; DB_PASSWORD = clave; DB_PORT = puerto
        try:
            engine = create_engine(f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
            print(f"Conexión a PostgreSQL: {db} exitosa ✅")
            return engine
        except Exception as e:
            print(f"Error en conexión DB (Santa Fe): {e}"); return None
engine = conexionDB()

def InsertarDF(engine=engine,df=pd.DataFrame(),nombre="general"):
    for i in range(3):
        try:
            ###--->Consulta de inserción
            df.to_sql(name=nombre.lower(),con=engine,if_exists="replace",index=False)
            print(f"✅ Inserción exitosa: {nombre}")
            break
        except Exception as e:
            print(f"❌ No se pudo insertar: {e}")
            
def LeerTabla(engine=engine,tabla="general"):
    query = text(f"SELECT * FROM {tabla.lower()};")
    ###--->Consulta de lectura
    for i in range(3):

        try:
            with engine.begin() as conn:
                    resultado = conn.execute(query)
                    filas = resultado.fetchall()
                    columnas = resultado.keys()
                    lectura = pd.DataFrame(filas,columns=columnas)
                    break
        except Exception as e:
                    print(f"❌ No se encontró la tabla: {e}")
                    time.sleep(5)
        
    return lectura

def BorrarTabla(engine=engine,tabla="general"):
    # ###--->Consulta de borrado de tabla
    borrar = text(f"DROP TABLE IF EXISTS {tabla.lower()} ")  ##Primero se elimina la tabla si existe
    for i in range(3):
        try:
            with engine.begin() as conn:
                conn.execute(borrar)
                print("✅ Borrado exitoso")
                break
        except Exception as e:
                print(f"❌ Error al borrar: {e}")
