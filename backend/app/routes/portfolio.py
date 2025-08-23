from flask import jsonify, Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User, Holding, Transaction, TransactionType
from app import db
from decimal import Decimal
from marshmallow import ValidationError
from app.schemas import TradeSchema

portfolio_bp = Blueprint('portfolio', __name__, url_prefix='/api/portfolio')
trade_schema = TradeSchema()

@portfolio_bp.route('', methods=['GET'])
@jwt_required()
def get_portfolio():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user or not user.portfolio:
        return jsonify({"error": "Portfolio not found"}), 404

    holdings_data = [{
        "ticker": h.ticker_symbol,
        "quantity": str(h.quantity),
        "average_purchase_price": str(h.average_purchase_price)
    } for h in user.portfolio.holdings]

    return jsonify({
        "cash_balance": str(user.portfolio.cash_balance),
        "holdings": holdings_data
    }), 200

# --- Placeholder para el servicio de mercado ---
# TODO: Reemplazar esto con una llamada real a una API de mercado (ej. Financial Modeling Prep)
def get_market_price(ticker):
    """
    Función simulada para obtener el precio de un activo.
    Devuelve un precio fijo para fines de prueba.
    """
    # Precios de ejemplo para simulación
    mock_prices = {
        "AAPL": Decimal("175.50"),
        "GOOGL": Decimal("140.20"),
        "TSLA": Decimal("250.00")
    }
    price = mock_prices.get(ticker.upper())
    if price is None:
        raise ValueError(f"Ticker '{ticker}' not found")
    return price
# ---------------------------------------------

@portfolio_bp.route('/buy', methods=['POST'])
@jwt_required()
def buy_asset():
    """
    Permite a un usuario autenticado comprar un activo.
    Espera un JSON con: {"ticker": "AAPL", "quantity": 10}
    """
    try:
        data = trade_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify(err.messages), 422

    ticker = data['ticker']
    quantity = data['quantity']
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    try:
        price = get_market_price(ticker)
    except ValueError as e:
        # Usamos 404 Not Found, que es más específico para un recurso que no existe.
        return jsonify({"error": f"Ticker '{ticker}' not found"}), 404

    total_cost = price * quantity

    if user.portfolio.cash_balance < total_cost:
        return jsonify({"error": "Insufficient funds"}), 400

    # Actualizar el balance de efectivo
    user.portfolio.cash_balance -= total_cost

    # Buscar si el activo ya existe en la cartera
    holding = Holding.query.filter_by(portfolio_id=user.portfolio.id, ticker_symbol=ticker).first()

    if holding:
        # Si ya existe, actualizamos el promedio y la cantidad
        new_quantity = holding.quantity + quantity
        new_avg_price = ((holding.average_purchase_price * holding.quantity) + total_cost) / new_quantity
        holding.quantity = new_quantity
        holding.average_purchase_price = new_avg_price
    else:
        # Si no, creamos un nuevo holding
        new_holding = Holding(
            portfolio_id=user.portfolio.id,
            ticker_symbol=ticker,
            quantity=quantity,
            average_purchase_price=price
        )
        db.session.add(new_holding)

    # Registrar la transacción
    new_transaction = Transaction(
        portfolio_id=user.portfolio.id,
        ticker_symbol=ticker,
        type=TransactionType.BUY,
        quantity=quantity,
        price_per_share=price
    )
    db.session.add(new_transaction)

    db.session.commit()

    return jsonify({"message": f"Successfully bought {quantity} of {ticker}", "new_cash_balance": str(user.portfolio.cash_balance)}), 200


@portfolio_bp.route('/sell', methods=['POST'])
@jwt_required()
def sell_asset():
    """
    Permite a un usuario autenticado vender un activo.
    Espera un JSON con: {"ticker": "AAPL", "quantity": 5}
    """
    try:
        data = trade_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify(err.messages), 422

    ticker = data['ticker']
    quantity_to_sell = data['quantity']
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    # Primero, validamos que el ticker exista para dar un error 404 si no se encuentra.
    try:
        price = get_market_price(ticker)
    except ValueError:
        return jsonify({"error": f"Ticker '{ticker}' not found"}), 404

    holding = Holding.query.filter_by(portfolio_id=user.portfolio.id, ticker_symbol=ticker).first()

    # Ahora, verificamos si el usuario posee el activo y en la cantidad suficiente con mensajes de error específicos.
    if not holding:
        return jsonify({"error": "You do not own this asset"}), 400

    if holding.quantity < quantity_to_sell:
        return jsonify({"error": "You do not own enough of this asset to sell"}), 400

    total_sale_value = price * quantity_to_sell

    user.portfolio.cash_balance += total_sale_value
    holding.quantity -= quantity_to_sell

    if holding.quantity == 0:
        db.session.delete(holding)

    # Registrar la transacción
    new_transaction = Transaction(
        portfolio_id=user.portfolio.id,
        ticker_symbol=ticker,
        type=TransactionType.SELL,
        quantity=quantity_to_sell,
        price_per_share=price
    )
    db.session.add(new_transaction)

    db.session.commit()

    return jsonify({"message": f"Successfully sold {quantity_to_sell} of {ticker}", "new_cash_balance": str(user.portfolio.cash_balance)}), 200