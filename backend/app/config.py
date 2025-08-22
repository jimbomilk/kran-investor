import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'una-clave-secreta-muy-dificil-de-adivinar'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class TestConfig(Config):
    TESTING = True
    # Usar una base de datos SQLite en memoria para que los tests sean rápidos y aislados
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    # Usar una clave secreta simple para los tests
    SECRET_KEY = 'test-secret-key'