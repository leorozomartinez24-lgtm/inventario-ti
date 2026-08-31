import psycopg2
import streamlit as st

def get_connection():
    try:
        conn = psycopg2.connect(
            host=st.secrets["database"]["host"],
            database=st.secrets["database"]["database"],
            user=st.secrets["database"]["user"],
            password=st.secrets["database"]["password"],
            port=st.secrets["database"]["port"],
            sslmode=st.secrets["database"]["sslmode"]
        )
        return conn
    except Exception as e:
        st.error(f"Error conectando a la base de datos: {e}")
        return None

def ejecutar_query(query, params=None):
    conn = get_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute(query, params)
            conn.commit()
            cur.close()
            conn.close()
            return True
        except Exception as e:
            st.error(f"Error ejecutando query: {e}")
            return False

def obtener_datos(query, params=None):
    conn = get_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute(query, params)
            datos = cur.fetchall()
            columnas = [desc[0] for desc in cur.description]
            cur.close()
            conn.close()
            return datos, columnas
        except Exception as e:
            st.error(f"Error obteniendo datos: {e}")
            return [], []
    return [], []
