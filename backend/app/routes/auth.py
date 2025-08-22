from flask import request, jsonify, Blueprint
from .. import db, bcrypt
from ..models import User, Portfolio

# Creamos un Blueprint para las rutas de autenticación.
# El url_prefix nos permite anteponer '/api/auth' a todas las rutas de este blueprint.
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Endpoint para registrar un nuevo usuario.
    Espera un JSON con 'username', 'email' y 'password'.
    """
    data = request.get_json()

    # Validación de datos de entrada
    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({"error": "Missing required fields"}), 400

    # Comprobar si el usuario o el email ya existen
    if User.query.filter_by(username=data.get('username')).first():
        return jsonify({"error": "Username already exists"}), 409 # 409 Conflict
    
    if User.query.filter_by(email=data.get('email')).first():
        return jsonify({"error": "Email already exists"}), 409

    # Hashear la contraseña para no guardarla en texto plano
    hashed_password = bcrypt.generate_password_hash(data.get('password')).decode('utf-8')

    # Crear una nueva instancia de Usuario
    new_user = User(
        username=data.get('username'),
        email=data.get('email'),
        password_hash=hashed_password
    )

    # Crear la cartera inicial para el nuevo usuario
    # La relación en el modelo se encargará de asociarlos correctamente.
    new_user.portfolio = Portfolio()

    # Añadir a la base de datos y guardar los cambios
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User created successfully"}), 201