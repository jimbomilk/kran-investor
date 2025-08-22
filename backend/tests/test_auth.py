import json
#
def test_register_success(client):
    """
    GIVEN una aplicación Flask configurada para pruebas
    WHEN se hace un POST a '/api/auth/register' con datos válidos
    THEN se debe devolver un código de estado 201 y un mensaje de éxito
    """
    response = client.post('/api/auth/register',
                                data=json.dumps(dict(
                                    username='testuser',
                                    email='test@example.com',
                                    password='password123'
                                )),
                                content_type='application/json')
    assert response.status_code == 201
    assert b"User created successfully" in response.data

def test_register_existing_user(client):
    """
    GIVEN un usuario que ya existe en la base de datos
    WHEN se intenta registrar de nuevo con el mismo email o username
    THEN se debe devolver un código de estado 409 (Conflicto)
    """
    # Primero, registramos un usuario
    client.post('/api/auth/register',
                     data=json.dumps(dict(
                         username='testuser',
                         email='test@example.com',
                         password='password123'
                     )),
                     content_type='application/json')
    
    # Intentamos registrarlo de nuevo
    response = client.post('/api/auth/register',
                                data=json.dumps(dict(
                                    username='testuser',
                                    email='another@email.com',
                                    password='password123'
                                )),
                                content_type='application/json')
    assert response.status_code == 409
    assert b"Username already exists" in response.data

def test_login_success(client):
    """
    GIVEN un usuario registrado
    WHEN se hace un POST a '/api/auth/login' con las credenciales correctas
    THEN se debe devolver un código de estado 200 y un token de acceso
    """
    # Primero, registramos un usuario
    client.post('/api/auth/register',
                     data=json.dumps(dict(
                         username='testuser',
                         email='test@example.com',
                         password='password123'
                     )),
                     content_type='application/json')

    # Hacemos login
    response = client.post('/api/auth/login',
                                data=json.dumps(dict(
                                    email='test@example.com',
                                    password='password123'
                                )),
                                content_type='application/json')
    
    data = json.loads(response.data)
    assert response.status_code == 200
    assert 'access_token' in data