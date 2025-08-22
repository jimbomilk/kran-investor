import enum
from datetime import datetime
from . import db # Importamos la instancia db desde __init__.py

class TransactionType(enum.Enum):
    BUY = 'BUY'
    SELL = 'SELL'

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    
    portfolio = db.relationship('Portfolio', back_populates='user', uselist=False, cascade="all, delete-orphan")

class Portfolio(db.Model):
    __tablename__ = 'portfolios'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    cash_balance = db.Column(db.Numeric(19, 4), nullable=False, default=100000.00)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), onupdate=db.func.now())

    user = db.relationship('User', back_populates='portfolio')
    holdings = db.relationship('Holding', back_populates='portfolio', cascade="all, delete-orphan")
    transactions = db.relationship('Transaction', back_populates='portfolio', cascade="all, delete-orphan")

class Holding(db.Model):
    __tablename__ = 'holdings'
    id = db.Column(db.Integer, primary_key=True)
    portfolio_id = db.Column(db.Integer, db.ForeignKey('portfolios.id'), nullable=False)
    ticker_symbol = db.Column(db.String(10), nullable=False)
    quantity = db.Column(db.Numeric(19, 4), nullable=False)
    average_purchase_price = db.Column(db.Numeric(19, 4), nullable=False)

    portfolio = db.relationship('Portfolio', back_populates='holdings')
    __table_args__ = (db.UniqueConstraint('portfolio_id', 'ticker_symbol', name='_portfolio_ticker_uc'),)

class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    portfolio_id = db.Column(db.Integer, db.ForeignKey('portfolios.id'), nullable=False)
    ticker_symbol = db.Column(db.String(10), nullable=False)
    type = db.Column(db.Enum(TransactionType), nullable=False)
    quantity = db.Column(db.Numeric(19, 4), nullable=False)
    price_per_share = db.Column(db.Numeric(19, 4), nullable=False)
    transaction_date = db.Column(db.DateTime(timezone=True), server_default=db.func.now())

    portfolio = db.relationship('Portfolio', back_populates='transactions')