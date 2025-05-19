from typing import Optional
from datetime import datetime
from enum import Enum
from pydantic import Field
from app.models.base import MongoBaseModel

class TradeType(str, Enum):
    BUY = "BUY"
    SELL = "SELL"

class TradeStatus(str, Enum):
    PENDING = "PENDING"
    EXECUTED = "EXECUTED"
    CANCELLED = "CANCELLED"

class Trade(MongoBaseModel):
    user_id: str
    symbol: str
    trade_type: TradeType
    quantity: int
    price: float
    total_amount: float
    status: TradeStatus = TradeStatus.PENDING
    executed_at: Optional[datetime] = None
    profit_loss: Optional[float] = None

class TradeCreate(MongoBaseModel):
    symbol: str
    trade_type: TradeType
    quantity: int
    price: float

class TradeUpdate(MongoBaseModel):
    status: Optional[TradeStatus] = None
    executed_at: Optional[datetime] = None
    profit_loss: Optional[float] = None

class Portfolio(MongoBaseModel):
    user_id: str
    holdings: dict = Field(default_factory=dict)  # {symbol: quantity}
    cash_balance: float
    total_value: float
    last_updated: datetime = Field(default_factory=datetime.utcnow) 