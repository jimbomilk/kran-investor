import pytest
from app import create_app, db
from app.config import TestConfig # Importar la nueva configuración de test

@pytest.fixture(scope='module')
def test_app():
    """Crea y configura una instancia de la aplicación Flask para pruebas."""
    # Usamos la configuración de TestConfig para crear la app
    app = create_app(config_class=TestConfig)

    with app.app_context():
        db.create_all()  # Crea todas las tablas en la BD en memoria
        yield app        # La aplicación está disponible para las pruebas
        db.drop_all()    # Limpia la BD después de que terminen las pruebas del módulo

@pytest.fixture()
def test_client(test_app):
    """Crea un cliente de pruebas para la aplicación."""
    return test_app.test_client()
