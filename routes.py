from flask import Blueprint, request, jsonify, current_app
from psycopg2 import Error as Psycopg2Error
from db import get_db_connection

# Crear un Blueprint para las rutas de contactos
contactos_bp = Blueprint('contactos', __name__)

@contactos_bp.route('/contactos', methods=['GET'])
def obtener_contactos():
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        search_term = request.args.get('search')
        sql_query = 'SELECT id, nombre, telefono, email, created_at FROM contactos'
        params = []

        if search_term:
            sql_query += ' WHERE nombre ILIKE %s OR telefono ILIKE %s OR email ILIKE %s'
            params = [f'%{search_term}%', f'%{search_term}%', f'%{search_term}%']

        cur.execute(sql_query, params)
        contactos_raw = cur.fetchall()
        cur.close()

        contactos = []
        for c in contactos_raw:
            contactos.append({
                "id": c[0],
                "nombre": c[1],
                "telefono": c[2],
                "email": c[3],
                "created_at": c[4].isoformat() if c[4] else None
            })
        return jsonify(contactos)
    except Psycopg2Error as e:
        current_app.logger.error(f"Error al obtener contactos de la BD: {e}")
        return jsonify({"error": "Error interno del servidor al obtener contactos"}), 500

@contactos_bp.route('/contactos/<int:contact_id>', methods=['PUT'])
def modificar_contacto(contact_id):
    try:
        if not request.is_json:
            return jsonify({"error": "Content-Type debe ser application/json"}), 400

        data = request.get_json()

        # Construir la consulta UPDATE dinámicamente
        set_clauses = []
        params = []

        if 'nombre' in data:
            if not isinstance(data['nombre'], str) or not data['nombre'].strip():
                return jsonify({"error": "El campo 'nombre' es inválido si está presente"}), 400
            set_clauses.append("nombre = %s")
            params.append(data['nombre'])
        
        if 'telefono' in data:
            if data['telefono'] is not None and (not isinstance(data['telefono'], str) or not data['telefono'].strip()):
                return jsonify({"error": "El campo 'telefono' es inválido si está presente"}), 400
            set_clauses.append("telefono = %s")
            params.append(data['telefono'])
        else: # Permitir establecer telefono a NULL si no se envía y no es requerido
            set_clauses.append("telefono = NULL")

        if 'email' in data:
            if data['email'] is not None and (not isinstance(data['email'], str) or not data['email'].strip()):
                return jsonify({"error": "El campo 'email' es inválido si está presente"}), 400
            set_clauses.append("email = %s")
            params.append(data['email'])
        else: # Permitir establecer email a NULL si no se envía y no es requerido
            set_clauses.append("email = NULL")

        if not set_clauses:
            return jsonify({"error": "No se proporcionaron campos para actualizar"}), 400

        sql_query = f"UPDATE contactos SET {', '.join(set_clauses)} WHERE id = %s RETURNING id;"
        params.append(contact_id)

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(sql_query, params)
        updated_id = cur.fetchone()
        conn.commit()
        cur.close()

        if updated_id:
            return jsonify({"mensaje": f"Contacto con ID {contact_id} actualizado"}), 200
        else:
            return jsonify({"error": "Contacto no encontrado"}), 404

    except Psycopg2Error as e:
        current_app.logger.error(f"Error al modificar contacto en la BD: {e}")
        if 'conn' in locals() and conn:
            conn.rollback()
        return jsonify({"error": "Error interno del servidor al modificar contacto"}), 500
    except Exception as e:
        current_app.logger.error(f"Error inesperado al modificar contacto: {e}")
        return jsonify({"error": "Error inesperado al procesar la solicitud"}), 500

@contactos_bp.route('/contactos', methods=['POST'])
# @jwt_required() # Proteger esta ruta (temporalmente deshabilitado para depuración)
def agregar_contacto():
    try:
        if not request.is_json:
            return jsonify({"error": "Content-Type debe ser application/json"}), 400

        nuevo = request.get_json()

        # 'nombre' es obligatorio
        if 'nombre' not in nuevo or not isinstance(nuevo['nombre'], str) or not nuevo['nombre'].strip():
            return jsonify({"error": "El campo 'nombre' es obligatorio y debe ser una cadena no vacía"}), 400

        nombre = nuevo['nombre']
        telefono = nuevo.get('telefono') # .get() para campos opcionales
        email = nuevo.get('email')     # .get() para campos opcionales

        # Validar 'telefono' si está presente
        if telefono is not None and (not isinstance(telefono, str) or not telefono.strip()):
            return jsonify({"error": "El campo 'telefono' es inválido si está presente"}), 400
        
        # Validar 'email' si está presente
        if email is not None and (not isinstance(email, str) or not email.strip()):
            return jsonify({"error": "El campo 'email' es inválido si está presente"}), 400

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO contactos (nombre, telefono, email) VALUES (%s, %s, %s);', (nombre, telefono, email))
        conn.commit()
        cur.close()
        return jsonify({"mensaje": "Contacto agregado"}), 201
    except Psycopg2Error as e:
        current_app.logger.error(f"Error al agregar contacto a la BD: {e}")
        if 'conn' in locals() and conn:
            conn.rollback()
        return jsonify({"error": "Error interno del servidor al agregar contacto"}), 500

@contactos_bp.route('/contactos/<int:contact_id>', methods=['DELETE'])
def eliminar_contacto(contact_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('DELETE FROM contactos WHERE id = %s RETURNING id;', (contact_id,))
        deleted_id = cur.fetchone()
        conn.commit()
        cur.close()

        if deleted_id:
            return jsonify({"mensaje": f"Contacto con ID {contact_id} eliminado"}), 200
        else:
            return jsonify({"error": "Contacto no encontrado"}), 404

    except Psycopg2Error as e:
        current_app.logger.error(f"Error al eliminar contacto de la BD: {e}")
        if 'conn' in locals() and conn:
            conn.rollback()
        return jsonify({"error": "Error interno del servidor al eliminar contacto"}), 500
    except Exception as e:
        current_app.logger.error(f"Error inesperado al eliminar contacto: {e}")
        return jsonify({"error": "Error inesperado al procesar la solicitud"}), 500
