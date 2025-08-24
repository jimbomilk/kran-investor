import json
from decimal import Decimal
from unittest.mock import patch
from flask_jwt_extended import create_access_token

from app.models import User, Portfolio, Holding, Transaction, TransactionType
from app import db

# --- Helper ---
def get_auth_headers(user_id):
    """Genera cabeceras de autenticación para un ID de usuario."""
    access_token = create_access_token(identity=user_id)
    return {'Authorization': f'Bearer {access_token}'}


# --- Tests para el endpoint /buy ---

@patch('app.routes.portfolio_routes.MarketService.get_quote')
def test_buy_asset_success(mock_get_quote, client, test_user):
    """
    GIVEN un usuario autenticado con fondos suficientes.
    WHEN se envía una petición POST a /api/portfolio/buy.
    THEN se debe añadir el activo, deducir el dinero y registrar la transacción.
    """
    mock_get_quote.return_value = {'price': 150.00, 'symbol': 'AAPL'}
    headers = get_auth_headers(test_user.id)
    payload = {"ticker": "AAPL", "quantity": "10"}

    initial_cash = test_user.portfolio.cash_balance

    response = client.post('/api/portfolio/buy', headers=headers, json=payload)
    data = response.get_json()

    assert response.status_code == 200
    assert data['msg'] == "Compra de 10 acciones de AAPL a $150.00 realizada con éxito"

    db.session.refresh(test_user.portfolio)

    # Verificar saldo
    expected_cost = Decimal("150.00") * 10
    assert test_user.portfolio.cash_balance == initial_cash - expected_cost

    # Verificar holding
    holding = Holding.query.filter_by(portfolio_id=test_user.portfolio.id, ticker_symbol="AAPL").first()
    assert holding is not None
    assert holding.quantity == 10
    assert holding.average_purchase_price == Decimal("150.00")

    # Verificar transacción
    transaction = Transaction.query.filter_by(portfolio_id=test_user.portfolio.id, ticker_symbol="AAPL").first()
    assert transaction is not None
    assert transaction.type == TransactionType.BUY
    assert transaction.quantity == 10
    assert transaction.price_per_share == Decimal("150.00")


@patch('app.routes.portfolio_routes.MarketService.get_quote')
def test_buy_asset_insufficient_funds(mock_get_quote, client, test_user):
    """
    GIVEN un usuario autenticado.
    WHEN intenta comprar un activo por un valor mayor a su saldo.
    THEN la API debe devolver un error 400.
    """
    mock_get_quote.return_value = {'price': 15000.00, 'symbol': 'AMZN'}
    headers = get_auth_headers(test_user.id)
    payload = {"ticker": "AMZN", "quantity": "10"} # Costo > 100,000

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
    mock_get_quote.return_value = None
    headers = get_auth_headers(test_user.id)
    payload = {"ticker": "INVALIDTICKER", "quantity": "10"}

    response = client.post('/api/portfolio/buy', headers=headers, json=payload)
    data = response.get_json()

    assert response.status_code == 404
    assert data['msg'] == "No se pudo obtener la cotización para el ticker 'INVALIDTICKER'"


# --- Tests para el endpoint /sell ---

@patch('app.routes.portfolio_routes.MarketService.get_quote')
def test_sell_asset_success(mock_get_quote, client, test_user):
    """
    GIVEN un usuario autenticado que posee un activo.
    WHEN envía una petición POST a /api/portfolio/sell.
    THEN se debe vender el activo, añadir el dinero y registrar la transacción.
    """
    # Setup: Añadir un holding al portafolio del usuario
    holding = Holding(
        portfolio_id=test_user.portfolio.id,
        ticker_symbol="TSLA",
        quantity=Decimal("20"),
        average_purchase_price=Decimal("250.00")
    )
    db.session.add(holding)
    db.session.commit()

    mock_get_quote.return_value = {'price': 300.00, 'symbol': 'TSLA'}
    headers = get_auth_headers(test_user.id)
    payload = {"ticker": "TSLA", "quantity": "5"}

    initial_cash = test_user.portfolio.cash_balance

    response = client.post('/api/portfolio/sell', headers=headers, json=payload)
    data = response.get_json()

    assert response.status_code == 200
    assert data['msg'] == "Venta de 5 acciones de TSLA a $300.00 realizada con éxito"

    db.session.refresh(test_user.portfolio)
    db.session.refresh(holding)

    # Verificar saldo
    expected_gain = Decimal("300.00") * 5
    assert test_user.portfolio.cash_balance == initial_cash + expected_gain

    # Verificar holding
    assert holding.quantity == 15 # 20 - 5

    # Verificar transacción
    transaction = Transaction.query.filter_by(portfolio_id=test_user.portfolio.id, type=TransactionType.SELL).first()
    assert transaction is not None
    assert transaction.quantity == 5
    assert transaction.price_per_share == Decimal("300.00")


@patch('app.routes.portfolio_routes.MarketService.get_quote')
def test_sell_all_of_asset_success(mock_get_quote, client, test_user):
    """
    GIVEN un usuario autenticado que posee un activo.
    WHEN vende la cantidad total de ese activo.
    THEN el holding debe ser eliminado de la base de datos.
    """
    holding = Holding(
        portfolio_id=test_user.portfolio.id,
        ticker_symbol="MSFT",
        quantity=Decimal("10"),
        average_purchase_price=Decimal("400.00")
    )
    db.session.add(holding)
    db.session.commit()

    mock_get_quote.return_value = {'price': 450.00, 'symbol': 'MSFT'}
    headers = get_auth_headers(test_user.id)
    payload = {"ticker": "MSFT", "quantity": "10"}

    response = client.post('/api/portfolio/sell', headers=headers, json=payload)
    assert response.status_code == 200

    # Verificar que el holding fue eliminado
    deleted_holding = Holding.query.filter_by(portfolio_id=test_user.portfolio.id, ticker_symbol="MSFT").first()
    assert deleted_holding is None


@patch('app.routes.portfolio_routes.MarketService.get_quote')
def test_sell_asset_not_enough_quantity(mock_get_quote, client, test_user):
    """
    GIVEN un usuario autenticado que posee un activo.
    WHEN intenta vender más cantidad de la que posee.
    THEN la API debe devolver un error 400.
    """
    holding = Holding(
        portfolio_id=test_user.portfolio.id,
        ticker_symbol="NVDA",
        quantity=Decimal("5"),
        average_purchase_price=Decimal("800.00")
    )
    db.session.add(holding)
    db.session.commit()

    mock_get_quote.return_value = {'price': 900.00, 'symbol': 'NVDA'}
    headers = get_auth_headers(test_user.id)
    payload = {"ticker": "NVDA", "quantity": "10"} # Solo tiene 5

    response = client.post('/api/portfolio/sell', headers=headers, json=payload)
    data = response.get_json()

    assert response.status_code == 400
    assert data['msg'] == "No tienes suficientes acciones para vender"
    # A diferencia de antes, la validación ocurre DESPUÉS de llamar a la API de precios
    mock_get_quote.assert_called_once_with("NVDA")


def test_sell_asset_not_owned(client, test_user):
    """
    GIVEN un usuario autenticado.
    WHEN intenta vender un activo que no posee.
    THEN la API debe devolver un error 400.
    """
    headers = get_auth_headers(test_user.id)
    payload = {"ticker": "GOOGL", "quantity": "10"}

    response = client.post('/api/portfolio/sell', headers=headers, json=payload)
    data = response.get_json()

    assert response.status_code == 400
    assert data['msg'] == "No tienes suficientes acciones para vender"