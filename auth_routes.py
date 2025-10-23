from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from .db import create_user, get_user_by_username

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

@auth_bp.route('/login', methods=['POST'])
def login():
    username = request.json.get('username', None)
    password = request.json.get('password', None)

    if not username or not password:
        return jsonify({"msg": "Faltan nombre de usuario o contraseña"}), 400

    user = get_user_by_username(username)

    if user is None or not check_password_hash(user['password'], password):
        return jsonify({"msg": "Nombre de usuario o contraseña incorrectos"}), 401 # Unauthorized

    access_token = create_access_token(identity=user['id'])
    return jsonify(access_token=access_token)

# Ruta de ejemplo protegida (requiere JWT)
@auth_bp.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user_id = get_jwt_identity()
    return jsonify(logged_in_as=current_user_id), 200
