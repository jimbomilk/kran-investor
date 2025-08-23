from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from app.services.market_service import MarketService

# Usamos un prefijo de URL para mantener las rutas organizadas
market_bp = Blueprint('market_bp', __name__, url_prefix='/api/market')

@market_bp.route('/quote/<string:ticker>', methods=['GET'])
@jwt_required()
def get_ticker_quote(ticker):
    """
    Proporciona la última cotización para un ticker de acción específico.
    ---
    tags:
      - Market
    parameters:
      - name: ticker
        in: path
        type: string
        required: true
        description: El símbolo del ticker de la acción (ej. AAPL).
    responses:
      200:
        description: Datos de la cotización para el ticker.
      404:
        description: Ticker no encontrado.
    """
    if not ticker:
        return jsonify({"msg": "El símbolo del ticker es obligatorio"}), 400

    quote = MarketService.get_quote(ticker)

    if quote:
        return jsonify(quote)
    
    return jsonify({"msg": f"Ticker '{ticker}' no encontrado o error al obtener los datos."}), 404

@market_bp.route('/search/<string:query>', methods=['GET'])
@jwt_required()
def search_market_assets(query):
    """
    Busca activos (acciones) que coincidan con una cadena de consulta dada.
    ---
    tags:
      - Market
    parameters:
      - name: query
        in: path
        type: string
        required: true
        description: El término de búsqueda (ej. 'Apple').
    responses:
      200:
        description: Una lista de activos coincidentes.
    """
    if not query:
        return jsonify({"msg": "La consulta de búsqueda es obligatoria"}), 400

    results = MarketService.search_assets(query)
    return jsonify(results)