from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash
from db import create_user, get_user_by_username

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    username = request.json.get('username', None)
    password = request.json.get('password', None)

    if not username or not password:
        return jsonify({"msg": "Faltan nombre de usuario o contraseña"}), 400

    user_id = create_user(username, password)

    if user_id is None:
        return jsonify({"msg": "El nombre de usuario ya existe"}), 409 # Conflict

    return jsonify({"msg": "Usuario registrado exitosamente", "user_id": user_id}), 201
