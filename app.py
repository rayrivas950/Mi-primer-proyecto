from flask import Flask, request, jsonify, g
import psycopg2
from psycopg2 import Error as Psycopg2Error # Importar el tipo de error específico
import os
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager # Importar JWTManager

# Importar funciones de la base de datos desde el módulo db.py
from .db import get_db_connection, close_db_connection
# Importar el Blueprint de rutas desde el módulo routes.py
from .routes import contactos_bp
# Importar el Blueprint de autenticación desde el módulo auth_routes.py
from .auth_routes import auth_bp

load_dotenv()

app = Flask(__name__)

# Configurar la clave secreta para JWT desde las variables de entorno
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
# Inicializar Flask-JWT-Extended
jwt = JWTManager(app)

# Registrar la función de cierre de conexión con el contexto de la aplicación
@app.teardown_appcontext
def teardown_db(exception):
    close_db_connection(exception)

# Manejador global para errores 500 (errores internos del servidor)
@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f"Error interno del servidor: {error}")
    return jsonify({"error": "Ha ocurrido un error interno en el servidor."}), 500

# Registrar el Blueprint de contactos
app.register_blueprint(contactos_bp)
# Registrar el Blueprint de autenticación
app.register_blueprint(auth_bp)

if __name__ == '__main__':
    app.run(debug=True)
