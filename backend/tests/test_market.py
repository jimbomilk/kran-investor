from unittest.mock import patch
from flask_jwt_extended import create_access_token

# --- Helper ---
def get_auth_headers(user):
    """Genera cabeceras de autenticación para un usuario."""
    access_token = create_access_token(identity=user.id)
    return {'Authorization': f'Bearer {access_token}'}

# --- Tests para Market Routes ---

@patch('app.routes.market_routes.MarketService.get_quote')
def test_get_quote_success(mock_get_quote, client, test_user):
    """
    GIVEN un usuario autenticado y un ticker válido.
    WHEN se hace una petición a /api/market/quote/{ticker}.
    THEN se debe devolver la cotización del activo.
    """
    mock_get_quote.return_value = {"symbol": "AAPL", "price": 150.75, "name": "Apple Inc."}
    headers = get_auth_headers(test_user)
    response = client.get('/api/market/quote/AAPL', headers=headers)
    data = response.get_json()

    assert response.status_code == 200
    assert data['symbol'] == "AAPL"
    assert data['price'] == 150.75
    mock_get_quote.assert_called_once_with('AAPL')

@patch('app.routes.market_routes.MarketService.get_quote')
def test_get_quote_not_found(mock_get_quote, client, test_user):
    """
    GIVEN un usuario autenticado y un ticker inválido.
    WHEN se hace una petición a /api/market/quote/{ticker}.
    THEN se debe devolver un error 404.
    """
    mock_get_quote.return_value = None
    headers = get_auth_headers(test_user)
    response = client.get('/api/market/quote/INVALID', headers=headers)
    data = response.get_json()

    assert response.status_code == 404
    mock_get_quote.assert_called_once_with('INVALID')

def test_get_quote_unauthorized(client):
    """
    GIVEN un usuario no autenticado.
    WHEN se hace una petición a /api/market/quote/{ticker}.
    THEN se debe devolver un error 401.
    """
    response = client.get('/api/market/quote/AAPL')
    assert response.status_code == 401

@patch('app.routes.market_routes.MarketService.search_assets')
def test_search_assets_success(mock_search_assets, client, test_user):
    """
    GIVEN un usuario autenticado y una consulta de búsqueda.
    WHEN se hace una petición a /api/market/search/{query}.
    THEN se debe devolver una lista de activos.
    """
    mock_search_assets.return_value = [
        {"symbol": "AAPL", "name": "Apple Inc."},
        {"symbol": "APPL", "name": "Apple Hospitality REIT, Inc."}
    ]
    headers = get_auth_headers(test_user)
    response = client.get('/api/market/search/Apple', headers=headers)
    data = response.get_json()

    assert response.status_code == 200
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]['name'] == "Apple Inc."
    mock_search_assets.assert_called_once_with('Apple')

def test_search_assets_unauthorized(client):
    """
    GIVEN un usuario no autenticado.
    WHEN se hace una petición a /api/market/search/{query}.
    THEN se debe devolver un error 401.
    """
    response = client.get('/api/market/search/Apple')
    assert response.status_code == 401