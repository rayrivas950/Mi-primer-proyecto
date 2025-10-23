import psycopg2
import os
from flask import g
from werkzeug.security import generate_password_hash, check_password_hash # Importar utilidades de seguridad

# 🔗 Conexión a la base de datos
def get_db_connection():
    # Si la conexión no existe en el objeto 'g' (específico de la solicitud),
    # la creamos y la almacenamos.
    if 'db_conn' not in g:
        g.db_conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            database=os.getenv("DB_NAME", "contactosdb"),
            user=os.getenv("DB_USER", "raynor_user"),
            password=os.getenv("DB_PASS", "12345")
        )
    return g.db_conn

# Función para cerrar la conexión a la base de datos al finalizar la solicitud
def close_db_connection(exception):
    # Recuperamos la conexión de 'g' y la eliminamos.
    db = g.pop('db_conn', None)
    # Si la conexión existe, la cerramos.
    if db is not None:
        db.close()

# --- Funciones para la gestión de usuarios ---

def create_user(username, password):
    # Hashear la contraseña antes de almacenarla
    hashed_password = generate_password_hash(password)
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO users (username, password) VALUES (%s, %s) RETURNING id;",
            (username, hashed_password)
        )
        user_id = cur.fetchone()[0]
        conn.commit()
        return user_id
    except psycopg2.IntegrityError:
        # Manejar caso donde el username ya existe (UNIQUE constraint)
        conn.rollback()
        return None # Indica que el usuario ya existe
    finally:
        cur.close()

def get_user_by_username(username):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, username, password FROM users WHERE username = %s;", (username,))
        user_data = cur.fetchone()
        if user_data:
            # Devolver un diccionario para facilitar el acceso a los datos
            return {"id": user_data[0], "username": user_data[1], "password": user_data[2]}
        return None
    finally:
        cur.close()
