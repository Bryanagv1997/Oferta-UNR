import os
from dotenv import load_dotenv
import pandas as pd
import psycopg2

def fetch_general_table():
    """
    Conecta a la base de datos PostgreSQL y devuelve la tabla 'contratos' como un DataFrame de Pandas.
    """

    # Carga variables de entorno
    load_dotenv()

    # Conexión a la base de datos
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

    try:
        query = "SELECT * FROM contratos;"
        df = pd.read_sql(query, conn)
        return df
    except Exception as e:
        print(f"Error al consultar la tabla 'general': {e}")
        return pd.DataFrame()  # Devuelve un DataFrame vacío en caso de error
    finally:
        conn.close()
