from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from app.api.deps import get_current_active_user
from app.models.user import User
from app.models.stock import Stock, StockCreate, StockUpdate
from app.services.alpha_vantage import alpha_vantage
from app.db.mongodb import mongodb

router = APIRouter()

@router.get("/search")
async def search_stocks(
    query: str,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Search for stocks by symbol or company name
    """
    results = await alpha_vantage.search_symbols(query)
    return results

@router.get("/{symbol}")
async def get_stock(
    symbol: str,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get detailed stock information including real-time price and financial metrics
    """
    # Get real-time quote
    quote = await alpha_vantage.get_quote(symbol)
    if "Error Message" in quote:
        raise HTTPException(status_code=404, detail="Stock not found")
    
    # Get company overview
    overview = await alpha_vantage.get_company_overview(symbol)
    
    # Get financial statements
    income_stmt = await alpha_vantage.get_income_statement(symbol)
    balance_sheet = await alpha_vantage.get_balance_sheet(symbol)
    cash_flow = await alpha_vantage.get_cash_flow(symbol)
    
    # Get historical data
    historical = await alpha_vantage.get_daily_adjusted(symbol)
    
    return {
        "quote": quote,
        "overview": overview,
        "financial_statements": {
            "income_statement": income_stmt,
            "balance_sheet": balance_sheet,
            "cash_flow": cash_flow
        },
        "historical_data": historical
    }

@router.get("/{symbol}/historical")
async def get_historical_data(
    symbol: str,
    outputsize: str = Query("compact", regex="^(compact|full)$"),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get historical price data for a stock
    """
    data = await alpha_vantage.get_daily_adjusted(symbol, outputsize)
    if "Error Message" in data:
        raise HTTPException(status_code=404, detail="Stock not found")
    return data

@router.get("/{symbol}/financials")
async def get_financial_statements(
    symbol: str,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get financial statements (Income Statement, Balance Sheet, Cash Flow)
    """
    income_stmt = await alpha_vantage.get_income_statement(symbol)
    balance_sheet = await alpha_vantage.get_balance_sheet(symbol)
    cash_flow = await alpha_vantage.get_cash_flow(symbol)
    
    return {
        "income_statement": income_stmt,
        "balance_sheet": balance_sheet,
        "cash_flow": cash_flow
    }

@router.post("/watchlist/add/{symbol}")
async def add_to_watchlist(
    symbol: str,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Add a stock to user's watchlist
    """
    if symbol in current_user.watchlist:
        raise HTTPException(status_code=400, detail="Stock already in watchlist")
    
    await mongodb.get_collection("users").update_one(
        {"_id": current_user.id},
        {"$push": {"watchlist": symbol}}
    )
    
    return {"message": f"Added {symbol} to watchlist"}

@router.delete("/watchlist/remove/{symbol}")
async def remove_from_watchlist(
    symbol: str,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Remove a stock from user's watchlist
    """
    if symbol not in current_user.watchlist:
        raise HTTPException(status_code=400, detail="Stock not in watchlist")
    
    await mongodb.get_collection("users").update_one(
        {"_id": current_user.id},
        {"$pull": {"watchlist": symbol}}
    )
    
    return {"message": f"Removed {symbol} from watchlist"} 