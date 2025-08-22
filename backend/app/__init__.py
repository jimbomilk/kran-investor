from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from .config import Config

# Inicializamos las extensiones
db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
jwt = JWTManager()

def create_app(config_class=Config):
    """Fábrica para crear la instancia de la aplicación Flask."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Vinculamos las extensiones con la app
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)

    # Importamos y registramos los Blueprints
    from .routes.auth import auth_bp
    from .routes.portfolio import portfolio_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(portfolio_bp)

    return app