import json
from decimal import Decimal
from unittest.mock import patch
from flask_jwt_extended import create_access_token

from app.models import User, Holding, Transaction
from app import db

# --- Helper ---
def get_auth_headers(user):
    """Genera cabeceras de autenticación para un usuario."""
    # In the tests, the user object is not the same as the one from the DB,
    # so we need to get the ID from the object passed.
    access_token = create_access_token(identity=str(user.id))
    return {'Authorization': f'Bearer {access_token}'}


# --- Tests para el endpoint /buy ---

@patch('app.routes.portfolio_routes.MarketService.get_quote')
def test_buy_asset_success(mock_get_quote, client, test_user):
    """
    GIVEN un usuario autenticado con fondos suficientes.
    WHEN se envía una petición POST a /api/portfolio/buy.
    THEN se debe añadir el activo, deducir el dinero y registrar la transacción.
    """
    # Mock del servicio de mercado para devolver un precio fijo
    mock_get_quote.return_value = {'price': 150.00, 'symbol': 'AAPL'}

    headers = get_auth_headers(test_user)
    payload = {"ticker": "AAPL", "quantity": "10"}
    response = client.post('/api/portfolio/buy', headers=headers, json=payload)
    data = response.get_json()

    assert response.status_code == 200
    assert data['msg'] == "Compra de 10 acciones de AAPL a $150.00 realizada con éxito"

    # Verificar el estado de la base de datos
    db.session.refresh(test_user)
    # Dinero inicial: 10000. Coste: 150.00 * 10 = 1500.
    # Saldo final esperado: 10000 - 1500 = 8500
    assert test_user.virtual_cash == Decimal("8500.00")

    asset = Holding.query.filter_by(user_id=test_user.id, ticker="AAPL").first()
    assert asset is not None
    assert asset.quantity == 10

    transaction = Transaction.query.filter_by(user_id=test_user.id, ticker="AAPL").first()
    assert transaction is not None
    assert transaction.type == 'buy'
    assert transaction.quantity == 10
    assert transaction.price == Decimal("150.00")

@patch('app.routes.portfolio_routes.MarketService.get_quote')
def test_buy_asset_insufficient_funds(mock_get_quote, client, test_user):
    """
    GIVEN un usuario autenticado.
    WHEN intenta comprar un activo por un valor mayor a su saldo.
    THEN la API debe devolver un error 400.
    """
    mock_get_quote.return_value = {'price': 150.00, 'symbol': 'AAPL'}
    headers = get_auth_headers(test_user)
    # El usuario tiene 10000, la compra cuesta 150.00 * 100 = 15000
    payload = {"ticker": "AAPL", "quantity": "100"}
    response = client.post('/api/portfolio/buy', headers=headers, json=payload)
    data = response.get_json()

    assert response.status_code == 400
    assert data['msg'] == "Fondos insuficientes para realizar la compra"

@patch('app.routes.portfolio_routes.MarketService.get_quote')
def test_buy_asset_invalid_ticker(mock_get_quote, client, test_user):
    """
    GIVEN un usuario autenticado.
    WHEN intenta comprar un activo con un ticker inválido.
    THEN la API debe devolver un error 404.
    """
    mock_get_quote.return_value = None  # Simula que el ticker no fue encontrado
    headers = get_auth_headers(test_user)
    payload = {"ticker": "INVALIDTICKER", "quantity": "10"}
    response = client.post('/api/portfolio/buy', headers=headers, json=payload)
    data = response.get_json()

    assert response.status_code == 404
    assert "msg" in data
    assert "No se pudo obtener la cotización para el ticker 'INVALIDTICKER'" in data['msg']


# --- Tests para el endpoint /sell ---

@patch('app.routes.portfolio_routes.MarketService.get_quote')
def test_sell_asset_success(mock_get_quote, client, test_user):
    """
    GIVEN un usuario autenticado que posee un activo.
    WHEN envía una petición POST a /api/portfolio/sell.
    THEN se debe vender el activo, añadir el dinero y registrar la transacción.
    """
    # Setup: Darle al usuario un activo para vender
    asset = Holding(
        user_id=test_user.id,
        ticker="TSLA",
        quantity=Decimal("20"),
    )
    db.session.add(asset)
    db.session.commit()

    # Mock del servicio de mercado
    mock_get_quote.return_value = {'price': 250.00, 'symbol': 'TSLA'}

    headers = get_auth_headers(test_user)
    payload = {"ticker": "TSLA", "quantity": "5"}
    response = client.post('/api/portfolio/sell', headers=headers, json=payload)
    data = response.get_json()

    assert response.status_code == 200
    assert data['msg'] == "Venta de 5 acciones de TSLA a $250.00 realizada con éxito"

    # Verificar el estado de la base de datos
    db.session.refresh(test_user)
    # Dinero inicial: 10000. Venta: 250.00 * 5 = 1250.
    # Saldo final esperado: 10000 + 1250 = 11250.00
    assert test_user.virtual_cash == Decimal("11250.00")

    updated_asset = Holding.query.get(asset.id)
    assert updated_asset.quantity == 15  # 20 - 5

@patch('app.routes.portfolio_routes.MarketService.get_quote')
def test_sell_all_of_asset_success(mock_get_quote, client, test_user):
    """
    GIVEN un usuario autenticado que posee un activo.
    WHEN vende la cantidad total de ese activo.
    THEN el holding debe ser eliminado de la base de datos.
    """
    asset = Holding(
        user_id=test_user.id,
        ticker="TSLA",
        quantity=Decimal("20"),
    )
    db.session.add(asset)
    db.session.commit()

    mock_get_quote.return_value = {'price': 250.00, 'symbol': 'TSLA'}

    headers = get_auth_headers(test_user)
    payload = {"ticker": "TSLA", "quantity": "20"}
    response = client.post('/api/portfolio/sell', headers=headers, json=payload)
    data = response.get_json()

    assert response.status_code == 200
    assert data['msg'] == "Venta de 20 acciones de TSLA a $250.00 realizada con éxito"

    # Verificar que el holding fue eliminado
    deleted_asset = Holding.query.filter_by(user_id=test_user.id, ticker="TSLA").first()
    assert deleted_asset is None

@patch('app.routes.portfolio_routes.MarketService.get_quote')
def test_sell_asset_not_enough_quantity(mock_get_quote, client, test_user):
    """
    GIVEN un usuario autenticado que posee un activo.
    WHEN intenta vender más cantidad de la que posee.
    THEN la API debe devolver un error 400.
    """
    asset = Holding(
        user_id=test_user.id,
        ticker="TSLA",
        quantity=Decimal("20"),
    )
    db.session.add(asset)
    db.session.commit()

    mock_get_quote.return_value = {'price': 250.00, 'symbol': 'TSLA'}

    headers = get_auth_headers(test_user)
    payload = {"ticker": "TSLA", "quantity": "25"} # Solo tiene 20
    response = client.post('/api/portfolio/sell', headers=headers, json=payload)
    data = response.get_json()

    assert response.status_code == 400
    assert "msg" in data
    assert data['msg'] == "No tienes suficientes acciones para vender"
    # La llamada al mock no debería ocurrir porque la validación es anterior
    mock_get_quote.assert_not_called()

def test_sell_asset_not_owned(client, test_user):
    """
    GIVEN un usuario autenticado.
    WHEN intenta vender un activo que no posee.
    THEN la API debe devolver un error 400.
    """
    headers = get_auth_headers(test_user)
    payload = {"ticker": "GOOGL", "quantity": "10"} # No posee GOOGL
    response = client.post('/api/portfolio/sell', headers=headers, json=payload)
    data = response.get_json()

    assert response.status_code == 400
    assert "msg" in data
    assert data["msg"] == "No tienes suficientes acciones para vender"

@patch('app.routes.portfolio_routes.MarketService.get_quote')
def test_sell_asset_owned_but_invalid_ticker(mock_get_quote, client, test_user):
    """
    GIVEN un usuario que posee un activo con un ticker inválido.
    WHEN intenta vender ese activo.
    THEN la API debe devolver un error 404 porque no puede obtener la cotización.
    """
    # Setup: Darle al usuario un activo con un ticker que el servicio no encontrará nunca
    asset = Holding(
        user_id=test_user.id,
        ticker="INVALIDTICKER",
        quantity=Decimal("10"),
    )
    db.session.add(asset)
    db.session.commit()

    mock_get_quote.return_value = None # El servicio no encuentra el ticker

    headers = get_auth_headers(test_user)
    payload = {"ticker": "INVALIDTICKER", "quantity": "10"}
    response = client.post('/api/portfolio/sell', headers=headers, json=payload)
    data = response.get_json()

    assert response.status_code == 404
    assert "msg" in data
    assert "No se pudo obtener la cotización para el ticker 'INVALIDTICKER'" in data['msg']
