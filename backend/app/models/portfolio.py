from typing import List, Optional
from pydantic import BaseModel
from app.models.base import MongoBaseModel

class PortfolioBase(BaseModel):
    name: str
    description: Optional[str] = None

class PortfolioCreate(PortfolioBase):
    pass

class Portfolio(PortfolioBase, MongoBaseModel):
    user_id: str
    cash_balance: float = 0.0
    total_value: float = 0.0 