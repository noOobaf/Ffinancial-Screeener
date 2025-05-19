from typing import Optional, List, Dict
from datetime import datetime
from pydantic import Field, BaseModel
from app.models.base import MongoBaseModel

class FinancialMetrics(MongoBaseModel):
    pe_ratio: Optional[float] = None
    roe: Optional[float] = None
    roce: Optional[float] = None
    market_cap: Optional[float] = None
    revenue: Optional[float] = None
    debt_equity: Optional[float] = None
    current_ratio: Optional[float] = None
    quick_ratio: Optional[float] = None
    dividend_yield: Optional[float] = None
    eps: Optional[float] = None

class HistoricalData(MongoBaseModel):
    date: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    adjusted_close: float

class StockBase(BaseModel):
    symbol: str
    name: str
    sector: Optional[str] = None
    industry: Optional[str] = None

class StockCreate(StockBase):
    pass

class Stock(StockBase, MongoBaseModel):
    current_price: float = 0.0
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    dividend_yield: Optional[float] = None
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    financial_metrics: FinancialMetrics = Field(default_factory=FinancialMetrics)
    historical_data: List[HistoricalData] = []
    financial_statements: Dict[str, Dict] = {}  # P&L, Balance Sheet, Cash Flow

class StockUpdate(MongoBaseModel):
    name: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    current_price: Optional[float] = None
    financial_metrics: Optional[FinancialMetrics] = None 