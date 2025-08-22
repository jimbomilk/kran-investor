import pytest
import sys
import os

# Añade el directorio raíz del backend (que contiene 'app' y 'tests') al sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db

@pytest.fixture(scope='module')
def test_app():
    """Crea una instancia de la aplicación Flask para pruebas."""
    app = create_app()
    app.config.update({
        "TESTING": True,
        # Usar una base de datos SQLite en memoria para las pruebas
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SECRET_KEY": "my-test-secret-key"
    })

    with app.app_context():
        db.create_all()  # Crea todas las tablas en la BD en memoria
        yield app        # La aplicación está disponible para las pruebas
        db.drop_all()    # Limpia la BD después de que terminen las pruebas del módulo

@pytest.fixture()
def test_client(test_app):
    """Crea un cliente de pruebas para la aplicación."""
    return test_app.test_client()