from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import Field, BaseModel
from app.models.base import MongoBaseModel

class ScreeningRule(MongoBaseModel):
    field: str  # e.g., "pe_ratio", "market_cap"
    operator: str  # e.g., "<", ">", "==", "!="
    value: float
    logical_operator: Optional[str] = None  # "AND" or "OR"

class ScreenerBase(BaseModel):
    name: str
    description: Optional[str] = None
    criteria: Dict[str, Any]

class Screener(ScreenerBase, MongoBaseModel):
    user_id: str
    results: List[str] = []  # List of stock symbols
    last_run: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_public: bool = False
    results_count: Optional[int] = None

class ScreenerCreate(ScreenerBase):
    pass

class ScreenerUpdate(MongoBaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    rules: Optional[List[ScreeningRule]] = None
    is_public: Optional[bool] = None

class ScreenerResult(MongoBaseModel):
    screener_id: str
    symbol: str
    matched_rules: List[str]  # List of rules that matched
    score: Optional[float] = None  # Optional relevance score
    created_at: datetime = Field(default_factory=datetime.utcnow) 