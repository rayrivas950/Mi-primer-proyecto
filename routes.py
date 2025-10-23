from flask import Blueprint, request, jsonify, current_app
from psycopg2 import Error as Psycopg2Error
from .db import get_db_connection
from flask_jwt_extended import jwt_required # Importar el decorador para proteger rutas

# Crear un Blueprint para las rutas de contactos
contactos_bp = Blueprint('contactos', __name__)

@contactos_bp.route('/contactos', methods=['GET'])
@jwt_required() # Proteger esta ruta
def obtener_contactos():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM contactos;')
        contactos = cur.fetchall()
        cur.close() # Aunque la conexión se cierra en teardown, el cursor debe cerrarse aquí
        return jsonify(contactos)
    except Psycopg2Error as e:
        # Manejo de errores específicos de la base de datos
        current_app.logger.error(f"Error al obtener contactos de la BD: {e}")
        return jsonify({"error": "Error interno del servidor al obtener contactos"}), 500

@contactos_bp.route('/contactos', methods=['POST'])
@jwt_required() # Proteger esta ruta
def agregar_contacto():
    nuevo = request.get_json()
    # --- Inicio del bloque try-except para manejo de errores de BD y validación --- #
    try:
        # Validar que el cuerpo de la solicitud sea JSON
        if not request.is_json:
            return jsonify({"error": "Content-Type debe ser application/json"}), 400

        # Validar la presencia de campos
        if 'nombre' not in nuevo or 'telefono' not in nuevo:
            return jsonify({"error": "Faltan campos requeridos: 'nombre' y 'telefono' son obligatorios"}), 400

        nombre = nuevo['nombre']
        telefono = nuevo['telefono']

        # Validar tipos de datos y que no estén vacíos
        if not isinstance(nombre, str) or not nombre.strip():
            return jsonify({"error": "El campo 'nombre' es inválido o está vacío"}), 400
        if not isinstance(telefono, str) or not telefono.strip():
            return jsonify({"error": "El campo 'telefono' es inválido o está vacío"}), 400

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO contactos (nombre, telefono) VALUES (%s, %s);', (nombre, telefono))
        conn.commit()
        cur.close() # Cerrar el cursor después de la operación
        return jsonify({"mensaje": "Contacto agregado"}), 201
    except Psycopg2Error as e:
        # Manejo de errores específicos de la base de datos
        current_app.logger.error(f"Error al agregar contacto a la BD: {e}")
        # Si hay un error en la BD, es buena práctica hacer rollback
        if 'conn' in locals() and conn:
            conn.rollback()
        return jsonify({"error": "Error interno del servidor al agregar contacto"}), 500
    except Exception as e:
        # Captura cualquier otra excepción inesperada
        current_app.logger.error(f"Error inesperado al agregar contacto: {e}")
        return jsonify({"error": "Error inesperado al procesar la solicitud"}), 500
