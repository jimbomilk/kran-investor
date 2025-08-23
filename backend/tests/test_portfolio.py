import json
from decimal import Decimal
from flask_jwt_extended import create_access_token

from app.models import Holding, Transaction, TransactionType
from app import db

# --- Helper ---
def get_auth_headers(user):
    """Genera cabeceras de autenticación para un usuario."""
    access_token = create_access_token(identity=user.id)
    return {'Authorization': f'Bearer {access_token}'}


# --- Tests para el endpoint /buy ---

def test_buy_asset_success(client, test_user):
    """
    GIVEN un usuario autenticado con fondos suficientes.
    WHEN se envía una petición POST a /api/portfolio/buy.
    THEN se debe añadir el activo, deducir el dinero y registrar la transacción.
    """
    headers = get_auth_headers(test_user)
    payload = {"ticker": "AAPL", "quantity": "10"}
    response = client.post('/api/portfolio/buy', headers=headers, data=json.dumps(payload), content_type='application/json')
    data = response.get_json()

    assert response.status_code == 200
    assert data['message'] == "Successfully bought 10 of AAPL"

    # Verificar el estado de la base de datos
    db.session.refresh(test_user)
    # Dinero inicial: 10000. Precio simulado de AAPL: 175.50. Coste: 1755.00.
    # Saldo final esperado: 10000 - 1755 = 8245
    assert test_user.portfolio.cash_balance == Decimal("8245.00")

    holding = Holding.query.filter_by(portfolio_id=test_user.portfolio.id, ticker_symbol="AAPL").first()
    assert holding is not None
    assert holding.quantity == 10
    assert holding.average_purchase_price == Decimal("175.50")

    transaction = Transaction.query.filter_by(portfolio_id=test_user.portfolio.id).first()
    assert transaction is not None
    assert transaction.type == TransactionType.BUY
    assert transaction.ticker_symbol == "AAPL"
    assert transaction.quantity == 10

def test_buy_asset_insufficient_funds(client, test_user):
    """
    GIVEN un usuario autenticado.
    WHEN intenta comprar un activo por un valor mayor a su saldo.
    THEN la API debe devolver un error 400 y el payload.
    """
    headers = get_auth_headers(test_user)
    # El usuario tiene 10000, la compra cuesta 175.50 * 100 = 17550
    payload = {"ticker": "AAPL", "quantity": "100"}
    response = client.post('/api/portfolio/buy', headers=headers, data=json.dumps(payload), content_type='application/json')
    data = response.get_json()

    assert response.status_code == 400
    assert "received_payload" in data
    assert data['error'] == "Insufficient funds"

def test_buy_asset_invalid_ticker(client, test_user):
    """
    GIVEN un usuario autenticado.
    WHEN intenta comprar un activo con un ticker inválido.
    THEN la API debe devolver un error 404.
    """
    headers = get_auth_headers(test_user)
    payload = {"ticker": "INVALIDTICKER", "quantity": "10"}
    response = client.post('/api/portfolio/buy', headers=headers, data=json.dumps(payload), content_type='application/json')
    data = response.get_json()

    assert response.status_code == 404
    assert "error" in data
    assert "not found" in data['error']


# --- Tests para el endpoint /sell ---

def test_sell_asset_success(client, test_user):
    """
    GIVEN un usuario autenticado que posee un activo.
    WHEN envía una petición POST a /api/portfolio/sell.
    THEN se debe vender el activo, añadir el dinero y registrar la transacción.
    """
    # Setup: Darle al usuario un activo para vender
    holding = Holding(
        portfolio_id=test_user.portfolio.id,
        ticker_symbol="TSLA",
        quantity=Decimal("20"),
        average_purchase_price=Decimal("240.00"),
    )
    db.session.add(holding)
    db.session.commit()

    headers = get_auth_headers(test_user)
    payload = {"ticker": "TSLA", "quantity": "5"}
    response = client.post('/api/portfolio/sell', headers=headers, data=json.dumps(payload), content_type='application/json')
    data = response.get_json()

    assert response.status_code == 200
    assert data['message'] == "Successfully sold 5 of TSLA"

    # Verificar el estado de la base de datos
    db.session.refresh(test_user)
    # Dinero inicial: 10000. Precio simulado de TSLA: 250.00. Venta: 1250.00.
    # Saldo final esperado: 10000 + 1250 = 11250
    assert test_user.portfolio.cash_balance == Decimal("11250.00")

    updated_holding = Holding.query.get(holding.id)
    assert updated_holding.quantity == 15  # 20 - 5

    transaction = Transaction.query.filter_by(type=TransactionType.SELL).first()
    assert transaction is not None
    assert transaction.ticker_symbol == "TSLA"

def test_sell_all_of_asset_success(client, test_user):
    """
    GIVEN un usuario autenticado que posee un activo.
    WHEN vende la cantidad total de ese activo.
    THEN el holding debe ser eliminado de la base de datos.
    """
    holding = Holding(
        portfolio_id=test_user.portfolio.id,
        ticker_symbol="TSLA",
        quantity=Decimal("20"),
        average_purchase_price=Decimal("240.00"),
    )
    db.session.add(holding)
    db.session.commit()

    headers = get_auth_headers(test_user)
    payload = {"ticker": "TSLA", "quantity": "20"}
    response = client.post('/api/portfolio/sell', headers=headers, data=json.dumps(payload), content_type='application/json')

    assert response.status_code == 200

    # Verificar que el holding fue eliminado
    deleted_holding = Holding.query.filter_by(ticker_symbol="TSLA").first()
    assert deleted_holding is None

def test_sell_asset_not_enough_quantity(client, test_user):
    """
    GIVEN un usuario autenticado que posee un activo.
    WHEN intenta vender más cantidad de la que posee.
    THEN la API debe devolver un error 400 y el payload.
    """
    holding = Holding(
        portfolio_id=test_user.portfolio.id,
        ticker_symbol="TSLA",
        quantity=Decimal("20"),
        average_purchase_price=Decimal("240.00"),
    )
    db.session.add(holding)
    db.session.commit()

    headers = get_auth_headers(test_user)
    payload = {"ticker": "TSLA", "quantity": "25"} # Solo tiene 20
    response = client.post('/api/portfolio/sell', headers=headers, data=json.dumps(payload), content_type='application/json')
    data = response.get_json()

    assert response.status_code == 400
    assert "received_payload" in data
    assert "error" in data
    assert data['error'] == "You do not own enough of this asset to sell"

def test_sell_asset_not_owned(client, test_user):
    """
    GIVEN un usuario autenticado.
    WHEN intenta vender un activo que no posee.
    THEN la API debe devolver un error 400 y el payload.
    """
    headers = get_auth_headers(test_user)
    payload = {"ticker": "GOOGL", "quantity": "10"} # No posee GOOGL
    response = client.post('/api/portfolio/sell', headers=headers, data=json.dumps(payload), content_type='application/json')
    data = response.get_json()

    assert response.status_code == 400
    assert "received_payload" in data
    assert "error" in data
    assert data['error'] == "You do not own this asset"

def test_sell_asset_invalid_ticker(client, test_user):
    """
    GIVEN un usuario autenticado.
    WHEN intenta vender un activo con un ticker inválido.
    THEN la API debe devolver un error 404.
    """
    headers = get_auth_headers(test_user)
    payload = {"ticker": "INVALIDTICKER", "quantity": "10"}
    response = client.post('/api/portfolio/sell', headers=headers, data=json.dumps(payload), content_type='application/json')
    data = response.get_json()

    assert response.status_code == 404
    assert "error" in data
    assert "not found" in data['error']