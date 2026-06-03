import mysql.connector
from mysql.connector import Error

DB_CONFIG = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': '101102',
    'database': 'Cable_Internet',
    'port': 3306
}

def conectar():
    try:
        conexion = mysql.connector.connect(**DB_CONFIG)
        return conexion
    except Error as e:
        print(f"Error de conexión: {e}")
        return None

def ejecutar_query(query, params=None, fetch_one=False, fetch_all=False, commit=False):
    conexion = conectar()
    if not conexion:
        return None

    cursor = conexion.cursor()
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        if fetch_one:
            resultado = cursor.fetchone()
        elif fetch_all:
            resultado = cursor.fetchall()
        elif commit:
            conexion.commit()
            resultado = cursor.lastrowid
        else:
            resultado = None

        return resultado
    except Error as e:
        print(f"Error en consulta: {e}")
        return None
    finally:
        cursor.close()
        conexion.close()