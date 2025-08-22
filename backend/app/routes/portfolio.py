from flask import jsonify, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User

portfolio_bp = Blueprint('portfolio', __name__, url_prefix='/api/portfolio')

@portfolio_bp.route('', methods=['GET'])
@jwt_required() # ¡Esta línea protege el endpoint!
def get_portfolio():
    """
    Devuelve los detalles de la cartera del usuario autenticado.
    """
    # Obtenemos la identidad del usuario desde el token JWT
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user or not user.portfolio:
        return jsonify({"error": "Portfolio not found"}), 404

    # Preparamos los datos para la respuesta JSON
    holdings_data = [
        {
            "ticker": holding.ticker_symbol,
            "quantity": str(holding.quantity), # Convertimos Decimal a string para JSON
            "average_price": str(holding.average_purchase_price)
        } for holding in user.portfolio.holdings
    ]

    return jsonify({
        "cash_balance": str(user.portfolio.cash_balance),
        "holdings": holdings_data
    }), 200