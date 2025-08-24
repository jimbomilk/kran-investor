from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User, Holding, Transaction
from app.services.market_service import MarketService
from app import db
import datetime
from decimal import Decimal

portfolio_bp = Blueprint('portfolio_bp', __name__, url_prefix='/api/portfolio')

@portfolio_bp.route('/buy', methods=['POST'])
@jwt_required()
def buy_asset():
    """
    Permite a un usuario comprar una cantidad de un activo usando su saldo virtual.
    Utiliza MarketService para obtener el precio real del activo.
    """
    data = request.get_json()
    ticker = data.get('ticker', '').upper()
    quantity = data.get('quantity')
    user_id = get_jwt_identity()

    if not all([ticker, quantity]):
        return jsonify({"msg": "El ticker y la cantidad son obligatorios"}), 400

    try:
        quantity = int(quantity)
        if quantity <= 0:
            raise ValueError
    except (ValueError, TypeError):
        return jsonify({"msg": "La cantidad debe ser un número entero positivo"}), 400

    # 1. Obtener cotización real desde el MarketService
    quote = MarketService.get_quote(ticker)
    if not quote or 'price' not in quote:
        return jsonify({"msg": f"No se pudo obtener la cotización para el ticker '{ticker}'"}), 404

    price = Decimal(quote['price'])
    total_cost = price * quantity
    user = User.query.get(user_id)
    portfolio = user.portfolio

    # 2. Validar fondos
    if portfolio.cash_balance < total_cost:
        return jsonify({"msg": "Fondos insuficientes para realizar la compra"}), 400

    # 3. Ejecutar la transacción
    portfolio.cash_balance -= total_cost
    
    holding = Holding.query.filter_by(portfolio_id=portfolio.id, ticker_symbol=ticker).first()
    
    if holding:
        # Calcular el nuevo precio promedio ponderado
        current_value = holding.quantity * holding.average_purchase_price
        new_value = quantity * price
        total_quantity = holding.quantity + quantity
        holding.average_purchase_price = (current_value + new_value) / total_quantity
        holding.quantity = total_quantity
    else:
        holding = Holding(
            portfolio_id=portfolio.id, 
            ticker_symbol=ticker, 
            quantity=quantity,
            average_purchase_price=price
        )
        db.session.add(holding)
        
    transaction = Transaction(
        portfolio_id=portfolio.id,
        ticker_symbol=ticker,
        quantity=quantity,
        price_per_share=price,
        type='BUY' # Usar el enum
    )
    db.session.add(transaction)

    db.session.commit()

    return jsonify({"msg": f"Compra de {quantity} acciones de {ticker} a ${price:.2f} realizada con éxito"}), 200


@portfolio_bp.route('/sell', methods=['POST'])
@jwt_required()
def sell_asset():
    """
    Permite a un usuario vender una cantidad de un activo que posee.
    Utiliza MarketService para obtener el precio real del activo.
    """
    data = request.get_json()
    ticker = data.get('ticker', '').upper()
    quantity_to_sell = data.get('quantity')
    user_id = get_jwt_identity()

    if not all([ticker, quantity_to_sell]):
        return jsonify({"msg": "El ticker y la cantidad son obligatorios"}), 400
    
    try:
        quantity_to_sell = int(quantity_to_sell)
        if quantity_to_sell <= 0:
            raise ValueError
    except (ValueError, TypeError):
        return jsonify({"msg": "La cantidad debe ser un número entero positivo"}), 400

    user = User.query.get(user_id)
    portfolio = user.portfolio

    # 1. Validar tenencia del activo
    holding = Holding.query.filter_by(portfolio_id=portfolio.id, ticker_symbol=ticker).first()
    if not holding or holding.quantity < quantity_to_sell:
        return jsonify({"msg": "No tienes suficientes acciones para vender"}), 400

    # 2. Obtener cotización real desde el MarketService
    quote = MarketService.get_quote(ticker)
    if not quote or 'price' not in quote:
        return jsonify({"msg": f"No se pudo obtener la cotización para el ticker '{ticker}'"}), 404

    price = Decimal(quote['price'])
    total_value = price * quantity_to_sell

    # 3. Ejecutar la transacción
    portfolio.cash_balance += total_value
    holding.quantity -= quantity_to_sell

    if holding.quantity == 0:
        db.session.delete(holding)
    
    # Registrar la transacción de venta
    transaction = Transaction(
        portfolio_id=portfolio.id,
        ticker_symbol=ticker,
        quantity=quantity_to_sell,
        price_per_share=price,
        type='SELL' # Usar el enum
    )
    db.session.add(transaction)
    
    db.session.commit()

    return jsonify({"msg": f"Venta de {quantity_to_sell} acciones de {ticker} a ${price:.2f} realizada con éxito"}), 200