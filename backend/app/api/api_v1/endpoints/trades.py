from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from app.api.deps import get_current_active_user
from app.models.user import User
from app.models.trade import Trade, TradeCreate, TradeUpdate, TradeType, TradeStatus
from app.services.alpha_vantage import alpha_vantage
from app.db.mongodb import mongodb
from datetime import datetime

router = APIRouter()

@router.post("/", response_model=Trade)
async def create_trade(
    trade_in: TradeCreate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Create a new paper trade
    """
    # Get current stock price
    quote = await alpha_vantage.get_quote(trade_in.symbol)
    if "Error Message" in quote:
        raise HTTPException(status_code=404, detail="Stock not found")
    
    current_price = float(quote["Global Quote"]["05. price"])
    total_amount = current_price * trade_in.quantity
    
    # Check if user has enough virtual capital for buy orders
    if trade_in.trade_type == TradeType.BUY:
        if total_amount > current_user.virtual_capital:
            raise HTTPException(
                status_code=400,
                detail="Insufficient virtual capital"
            )
    
    # Check if user has enough shares for sell orders
    if trade_in.trade_type == TradeType.SELL:
        portfolio = await mongodb.get_collection("portfolios").find_one(
            {"user_id": str(current_user.id)}
        )
        if not portfolio or portfolio["holdings"].get(trade_in.symbol, 0) < trade_in.quantity:
            raise HTTPException(
                status_code=400,
                detail="Insufficient shares"
            )
    
    # Create trade
    trade_dict = trade_in.dict()
    trade_dict.update({
        "user_id": str(current_user.id),
        "price": current_price,
        "total_amount": total_amount,
        "status": TradeStatus.PENDING,
        "created_at": datetime.utcnow()
    })
    
    result = await mongodb.get_collection("trades").insert_one(trade_dict)
    trade_dict["_id"] = result.inserted_id
    
    return Trade(**trade_dict)

@router.get("/", response_model=List[Trade])
async def list_trades(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    List user's trades
    """
    trades = await mongodb.get_collection("trades").find(
        {"user_id": str(current_user.id)}
    ).sort("created_at", -1).skip(skip).limit(limit).to_list(length=limit)
    
    return [Trade(**trade) for trade in trades]

@router.get("/{trade_id}", response_model=Trade)
async def get_trade(
    trade_id: str,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get a specific trade
    """
    trade = await mongodb.get_collection("trades").find_one({
        "_id": trade_id,
        "user_id": str(current_user.id)
    })
    
    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found")
    
    return Trade(**trade)

@router.post("/{trade_id}/execute")
async def execute_trade(
    trade_id: str,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Execute a pending trade
    """
    trade = await mongodb.get_collection("trades").find_one({
        "_id": trade_id,
        "user_id": str(current_user.id)
    })
    
    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found")
    
    if trade["status"] != TradeStatus.PENDING:
        raise HTTPException(status_code=400, detail="Trade is not pending")
    
    # Get current stock price
    quote = await alpha_vantage.get_quote(trade["symbol"])
    if "Error Message" in quote:
        raise HTTPException(status_code=404, detail="Stock not found")
    
    current_price = float(quote["Global Quote"]["05. price"])
    
    # Update trade status and price
    await mongodb.get_collection("trades").update_one(
        {"_id": trade_id},
        {
            "$set": {
                "status": TradeStatus.EXECUTED,
                "price": current_price,
                "total_amount": current_price * trade["quantity"],
                "executed_at": datetime.utcnow()
            }
        }
    )
    
    # Update portfolio
    portfolio = await mongodb.get_collection("portfolios").find_one(
        {"user_id": str(current_user.id)}
    )
    
    if not portfolio:
        portfolio = {
            "user_id": str(current_user.id),
            "holdings": {},
            "cash_balance": current_user.virtual_capital,
            "total_value": current_user.virtual_capital
        }
        await mongodb.get_collection("portfolios").insert_one(portfolio)
    
    # Update holdings and cash balance
    if trade["trade_type"] == TradeType.BUY:
        portfolio["holdings"][trade["symbol"]] = portfolio["holdings"].get(trade["symbol"], 0) + trade["quantity"]
        portfolio["cash_balance"] -= current_price * trade["quantity"]
    else:  # SELL
        portfolio["holdings"][trade["symbol"]] = portfolio["holdings"].get(trade["symbol"], 0) - trade["quantity"]
        portfolio["cash_balance"] += current_price * trade["quantity"]
    
    # Update total value
    total_value = portfolio["cash_balance"]
    for symbol, quantity in portfolio["holdings"].items():
        quote = await alpha_vantage.get_quote(symbol)
        if "Error Message" not in quote:
            price = float(quote["Global Quote"]["05. price"])
            total_value += price * quantity
    
    portfolio["total_value"] = total_value
    
    await mongodb.get_collection("portfolios").update_one(
        {"user_id": str(current_user.id)},
        {"$set": portfolio}
    )
    
    return {"message": "Trade executed successfully"} 