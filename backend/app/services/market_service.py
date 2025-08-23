import os
import requests
from functools import lru_cache

class MarketService:
    """
    Servicio para interactuar con la API de Financial Modeling Prep.
    """
    BASE_URL = "https://financialmodelingprep.com/api/v3"
    API_KEY = os.getenv("FMP_API_KEY")

    @staticmethod
    @lru_cache(maxsize=128)
    def get_quote(ticker: str):
        """
        Obtiene la cotización en tiempo real para un ticker dado.
        Cachea los resultados para evitar llamadas repetidas a la API para el mismo ticker.
        """
        if not MarketService.API_KEY:
            print("Aviso: FMP_API_KEY no está configurada. Usando datos de prueba para la cotización.")
            return {"symbol": ticker.upper(), "price": 150.00, "name": "Activo de Prueba"}

        try:
            url = f"{MarketService.BASE_URL}/quote/{ticker.upper()}?apikey={MarketService.API_KEY}"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            if data:
                return data[0]  # La API devuelve una lista con un elemento
            return None
        except requests.exceptions.RequestException as e:
            print(f"Error al obtener la cotización para {ticker}: {e}")
            return None

    @staticmethod
    def search_assets(query: str):
        """
        Busca activos (acciones, ETFs, etc.) que coincidan con una consulta.
        """
        if not MarketService.API_KEY:
            print("Aviso: FMP_API_KEY no está configurada. Usando datos de prueba para la búsqueda.")
            return [
                {"symbol": "AAPL", "name": "Apple Inc.", "currency": "USD", "stockExchange": "NASDAQ"},
                {"symbol": "AMZN", "name": "Amazon.com, Inc.", "currency": "USD", "stockExchange": "NASDAQ"},
            ]

        try:
            url = f"{MarketService.BASE_URL}/search-ticker?query={query}&limit=10&exchange=NASDAQ,NYSE&apikey={MarketService.API_KEY}"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error al buscar activos con la consulta '{query}': {e}")
            return []