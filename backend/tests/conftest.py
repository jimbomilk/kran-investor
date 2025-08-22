import pytest
from decimal import Decimal
from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

@pytest.fixture(scope='module')
def test_app():
    """
    Crea y configura una nueva instancia de la aplicación para los tests.
    Se ejecuta una vez por cada módulo de tests.
    """
    app = create_app()
    app.config.update({
        "TESTING": True,
        # Usa una base de datos SQLite en memoria para los tests
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "JWT_SECRET_KEY": "test-secret-key-for-testing"
    })

    with app.app_context():
        db.create_all()
        yield app  # Aquí es donde se ejecutan los tests
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='module')
def client(test_app):
    """Un cliente de prueba para la aplicación."""
    return test_app.test_client()

@pytest.fixture(scope='function')
def test_user(test_app):
    """
    Crea un nuevo usuario y su portafolio para cada test.
    Esto asegura que cada test comience con un estado limpio.
    """
    with test_app.app_context():
        # Se genera el hash de la contraseña directamente para evitar
        # posibles problemas con el método set_password en ciertos entornos.
        user = User(
            username='testuser',
            email='test@example.com',
            password_hash=generate_password_hash('password123')
        )
        user.portfolio.cash_balance = Decimal('10000.00')
        db.session.add(user)
        db.session.commit()

        yield user

        # Limpia la base de datos después de cada test
        db.session.delete(user)
        db.session.commit()