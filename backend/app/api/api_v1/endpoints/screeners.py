from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from app.api.deps import get_current_active_user
from app.models.user import User
from app.models.screener import Screener, ScreenerCreate, ScreenerUpdate, ScreeningRule
from app.services.alpha_vantage import alpha_vantage
from app.db.mongodb import mongodb
from datetime import datetime

router = APIRouter()

@router.post("/", response_model=Screener)
async def create_screener(
    screener_in: ScreenerCreate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Create a new stock screener
    """
    screener_dict = screener_in.dict()
    screener_dict["user_id"] = str(current_user.id)
    
    result = await mongodb.get_collection("screeners").insert_one(screener_dict)
    screener_dict["_id"] = result.inserted_id
    
    return Screener(**screener_dict)

@router.get("/", response_model=List[Screener])
async def list_screeners(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    List user's screeners
    """
    screeners = await mongodb.get_collection("screeners").find(
        {"user_id": str(current_user.id)}
    ).skip(skip).limit(limit).to_list(length=limit)
    
    return [Screener(**screener) for screener in screeners]

@router.get("/{screener_id}", response_model=Screener)
async def get_screener(
    screener_id: str,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get a specific screener
    """
    screener = await mongodb.get_collection("screeners").find_one({
        "_id": screener_id,
        "user_id": str(current_user.id)
    })
    
    if not screener:
        raise HTTPException(status_code=404, detail="Screener not found")
    
    return Screener(**screener)

@router.put("/{screener_id}", response_model=Screener)
async def update_screener(
    screener_id: str,
    screener_in: ScreenerUpdate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Update a screener
    """
    screener = await mongodb.get_collection("screeners").find_one({
        "_id": screener_id,
        "user_id": str(current_user.id)
    })
    
    if not screener:
        raise HTTPException(status_code=404, detail="Screener not found")
    
    update_data = screener_in.dict(exclude_unset=True)
    await mongodb.get_collection("screeners").update_one(
        {"_id": screener_id},
        {"$set": update_data}
    )
    
    updated_screener = await mongodb.get_collection("screeners").find_one({"_id": screener_id})
    return Screener(**updated_screener)

@router.delete("/{screener_id}")
async def delete_screener(
    screener_id: str,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Delete a screener
    """
    result = await mongodb.get_collection("screeners").delete_one({
        "_id": screener_id,
        "user_id": str(current_user.id)
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Screener not found")
    
    return {"message": "Screener deleted successfully"}

@router.post("/{screener_id}/run")
async def run_screener(
    screener_id: str,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Run a screener and get matching stocks
    """
    screener = await mongodb.get_collection("screeners").find_one({
        "_id": screener_id,
        "user_id": str(current_user.id)
    })
    
    if not screener:
        raise HTTPException(status_code=404, detail="Screener not found")
    
    # Get all stocks from database
    stocks = await mongodb.get_collection("stocks").find().to_list(length=None)
    
    # Apply screening rules
    matching_stocks = []
    for stock in stocks:
        matches = True
        for rule in screener["rules"]:
            field = rule["field"]
            operator = rule["operator"]
            value = rule["value"]
            
            stock_value = stock.get(field)
            if stock_value is None:
                matches = False
                break
            
            if operator == "<":
                if not (stock_value < value):
                    matches = False
                    break
            elif operator == ">":
                if not (stock_value > value):
                    matches = False
                    break
            elif operator == "==":
                if not (stock_value == value):
                    matches = False
                    break
            elif operator == "!=":
                if not (stock_value != value):
                    matches = False
                    break
        
        if matches:
            matching_stocks.append(stock)
    
    # Update screener with results
    await mongodb.get_collection("screeners").update_one(
        {"_id": screener_id},
        {
            "$set": {
                "last_run": datetime.utcnow(),
                "results_count": len(matching_stocks)
            }
        }
    )
    
    return {
        "screener_id": screener_id,
        "results_count": len(matching_stocks),
        "stocks": matching_stocks
    } 