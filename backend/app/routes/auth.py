from flask import request, jsonify, Blueprint
from flask_jwt_extended import create_access_token
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

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Endpoint para iniciar sesión.
    Espera un JSON con 'email' y 'password'.
    Devuelve un token de acceso JWT si las credenciales son correctas.
    """
    data = request.get_json()

    # 1. Validación de datos de entrada
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"error": "Email and password are required"}), 400

    # 2. Buscar al usuario por su email
    user = User.query.filter_by(email=data.get('email')).first()

    # 3. Verificar que el usuario existe y la contraseña es correcta
    if not user or not bcrypt.check_password_hash(user.password_hash, data.get('password')):
        return jsonify({"error": "Invalid credentials"}), 401  # 401 Unauthorized

    # 4. Crear el token de acceso JWT
    access_token = create_access_token(identity=user.id)

    # 5. Devolver el token
    return jsonify(access_token=access_token), 200