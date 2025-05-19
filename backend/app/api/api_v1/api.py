from fastapi import APIRouter
from app.api.api_v1.endpoints import (
    auth,
    users,
    stocks,
    screeners,
    trades,
    portfolio
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(stocks.router, prefix="/stocks", tags=["stocks"])
api_router.include_router(screeners.router, prefix="/screeners", tags=["screeners"])
api_router.include_router(trades.router, prefix="/trades", tags=["trades"])
api_router.include_router(portfolio.router, prefix="/portfolio", tags=["portfolio"]) 