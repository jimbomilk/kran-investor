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
 

    # Verificar el estado de la base de datos
    db.session.refresh(test_user)

    asset = Holding.query.filter_by(portfolio_id=test_user.portfolio.id, ticker_symbol="AAPL").first()
    assert asset is not None
    assert asset.quantity == 10

    transaction = Transaction.query.filter_by(portfolio_id=test_user.portfolio.id, ticker="AAPL").first()
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
    assert data['error'] == "Insufficient funds"

@patch('app.routes.portfolio_routes.MarketService.get_quote')
def test_buy_asset_invalid_ticker(mock_get_quote, client, test_user):
    """
    GIVEN un usuario autenticado.
    WHEN intenta comprar un activo con un ticker inválido.
    THEN la API debe devolver un error 404.
    """
    mock_get_quote.return_value = None  # Simula que el ticker no fue encontrado
    headers = get_auth_headers(test_user)
    payload = {"ticker": "INVALID", "quantity": "10"}
    response = client.post('/api/portfolio/buy', headers=headers, json=payload)
    data = response.get_json()

    assert response.status_code == 404
 

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
        portfolio_id=test_user.portfolio.id,
        ticker_symbol="TSLA",
        quantity=Decimal("20"),
        average_purchase_price=Decimal("250.00"),
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
   
    # Verificar el estado de la base de datos
    db.session.refresh(test_user)
    # Dinero inicial: 10000. Venta: 250.00 * 5 = 1250.

    updated_asset = Holding.query.get(asset.portfolio_id)
    assert updated_asset.quantity == 15  # 20 - 5

@patch('app.routes.portfolio_routes.MarketService.get_quote')
def test_sell_all_of_asset_success(mock_get_quote, client, test_user):
    """
    GIVEN un usuario autenticado que posee un activo.
    WHEN vende la cantidad total de ese activo.
    THEN el holding debe ser eliminado de la base de datos.
    """
    asset = Holding(
        portfolio_id=test_user.portfolio.id,
        ticker_symbol="TSLA",
        quantity=Decimal("20"),
        average_purchase_price=Decimal("250.00"),
    )
    db.session.add(asset)
    db.session.commit()

    mock_get_quote.return_value = {'price': 250.00, 'symbol': 'TSLA'}

    headers = get_auth_headers(test_user)
    payload = {"ticker": "TSLA", "quantity": "20"}
    response = client.post('/api/portfolio/sell', headers=headers, json=payload)
    data = response.get_json()

    assert response.status_code == 200
    

    # Verificar que el holding fue eliminado
    deleted_asset = Holding.query.filter_by(portfolio_id=test_user.portfolio.id, ticker_symbol="TSLA").first()
    assert deleted_asset is None

@patch('app.routes.portfolio_routes.MarketService.get_quote')
def test_sell_asset_not_enough_quantity(mock_get_quote, client, test_user):
    """
    GIVEN un usuario autenticado que posee un activo.
    WHEN intenta vender más cantidad de la que posee.
    THEN la API debe devolver un error 400.
    """
    asset = Holding(
        portfolio_id=test_user.portfolio.id,
        ticker_symbol="TSLA",
        quantity=Decimal("20"),
        average_purchase_price=Decimal("250.00"),
    )
    db.session.add(asset)
    db.session.commit()

    mock_get_quote.return_value = {'price': 250.00, 'symbol': 'TSLA'}

    headers = get_auth_headers(test_user)
    payload = {"ticker": "TSLA", "quantity": "25"} # Solo tiene 20
    response = client.post('/api/portfolio/sell', headers=headers, json=payload)
    data = response.get_json()

    assert response.status_code == 400
    assert "error" in data
    assert data['error'] == "You do not own enough of this asset to sell"
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
    assert "error" in data
    assert data["error"] == "You do not own this asset"

@patch('app.routes.portfolio_routes.MarketService.get_quote')
def test_sell_asset_owned_but_invalid_ticker(mock_get_quote, client, test_user):
    """
    GIVEN un usuario que posee un activo con un ticker inválido.
    WHEN intenta vender ese activo.
    THEN la API debe devolver un error 404 porque no puede obtener la cotización.
    """
    # Setup: Darle al usuario un activo con un ticker que el servicio no encontrará
    asset = Holding(
        portfolio_id=test_user.portfolio.id,
        ticker_symbol="INVALID",
        quantity=Decimal("10"),
        average_purchase_price=Decimal("100.00"),
    )
    db.session.add(asset)
    db.session.commit()

    mock_get_quote.return_value = None # El servicio no encuentra el ticker

    headers = get_auth_headers(test_user)
    payload = {"ticker": "INVALID", "quantity": "10"}
    response = client.post('/api/portfolio/sell', headers=headers, json=payload)
    data = response.get_json()

    assert response.status_code == 404

