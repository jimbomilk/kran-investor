from marshmallow import Schema, fields, validate
from decimal import Decimal

class TradeSchema(Schema):
    """
    Esquema para validar las operaciones de compra y venta.
    """
    ticker = fields.Str(required=True, error_messages={"required": "Ticker is required."})
    quantity = fields.Decimal(
        required=True,
        as_string=True,  # Permite recibir la cantidad como string y la convierte a Decimal
        validate=validate.Range(min=Decimal("0.000001"), error="Quantity must be a positive number.")
    )