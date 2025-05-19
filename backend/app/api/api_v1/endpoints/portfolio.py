from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from app.api.deps import get_current_active_user
from app.models.user import User
from app.models.trade import Portfolio
from app.services.alpha_vantage import alpha_vantage
from app.db.mongodb import mongodb
from datetime import datetime

router = APIRouter()

@router.get("/", response_model=Portfolio)
async def get_portfolio(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get user's portfolio
    """
    portfolio = await mongodb.get_collection("portfolios").find_one(
        {"user_id": str(current_user.id)}
    )
    
    if not portfolio:
        # Create new portfolio if it doesn't exist
        portfolio = {
            "user_id": str(current_user.id),
            "holdings": {},
            "cash_balance": current_user.virtual_capital,
            "total_value": current_user.virtual_capital,
            "last_updated": datetime.utcnow()
        }
        await mongodb.get_collection("portfolios").insert_one(portfolio)
    
    # Update portfolio value with current prices
    total_value = portfolio["cash_balance"]
    for symbol, quantity in portfolio["holdings"].items():
        quote = await alpha_vantage.get_quote(symbol)
        if "Error Message" not in quote:
            price = float(quote["Global Quote"]["05. price"])
            total_value += price * quantity
    
    portfolio["total_value"] = total_value
    portfolio["last_updated"] = datetime.utcnow()
    
    # Update portfolio in database
    await mongodb.get_collection("portfolios").update_one(
        {"user_id": str(current_user.id)},
        {"$set": portfolio}
    )
    
    return Portfolio(**portfolio)

@router.get("/holdings")
async def get_holdings(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get detailed holdings with current prices and P&L
    """
    portfolio = await mongodb.get_collection("portfolios").find_one(
        {"user_id": str(current_user.id)}
    )
    
    if not portfolio:
        return {"holdings": []}
    
    holdings = []
    for symbol, quantity in portfolio["holdings"].items():
        quote = await alpha_vantage.get_quote(symbol)
        if "Error Message" not in quote:
            current_price = float(quote["Global Quote"]["05. price"])
            market_value = current_price * quantity
            
            # Get average purchase price from trades
            trades = await mongodb.get_collection("trades").find({
                "user_id": str(current_user.id),
                "symbol": symbol,
                "status": "EXECUTED",
                "trade_type": "BUY"
            }).to_list(length=None)
            
            avg_price = 0
            if trades:
                total_cost = sum(trade["total_amount"] for trade in trades)
                total_quantity = sum(trade["quantity"] for trade in trades)
                avg_price = total_cost / total_quantity
            
            holdings.append({
                "symbol": symbol,
                "quantity": quantity,
                "current_price": current_price,
                "market_value": market_value,
                "average_price": avg_price,
                "unrealized_pnl": market_value - (avg_price * quantity) if avg_price > 0 else 0
            })
    
    return {"holdings": holdings}

@router.get("/performance")
async def get_performance(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get portfolio performance metrics
    """
    portfolio = await mongodb.get_collection("portfolios").find_one(
        {"user_id": str(current_user.id)}
    )
    
    if not portfolio:
        return {
            "total_value": current_user.virtual_capital,
            "cash_balance": current_user.virtual_capital,
            "invested_amount": 0,
            "unrealized_pnl": 0,
            "return_percentage": 0
        }
    
    # Calculate performance metrics
    total_value = portfolio["total_value"]
    cash_balance = portfolio["cash_balance"]
    invested_amount = total_value - cash_balance
    initial_capital = current_user.virtual_capital
    unrealized_pnl = total_value - initial_capital
    return_percentage = (unrealized_pnl / initial_capital) * 100 if initial_capital > 0 else 0
    
    return {
        "total_value": total_value,
        "cash_balance": cash_balance,
        "invested_amount": invested_amount,
        "unrealized_pnl": unrealized_pnl,
        "return_percentage": return_percentage
    } 