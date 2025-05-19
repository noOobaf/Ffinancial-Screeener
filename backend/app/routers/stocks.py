from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.models.stock import Stock, StockCreate
from app.db.mongodb import get_database

router = APIRouter()

@router.get("/", response_model=List[Stock])
async def get_stocks():
    db = await get_database()
    stocks = await db.stocks.find().to_list(length=100)
    return stocks

@router.post("/", response_model=Stock)
async def create_stock(stock: StockCreate):
    db = await get_database()
    stock_dict = stock.dict()
    result = await db.stocks.insert_one(stock_dict)
    stock_dict["id"] = str(result.inserted_id)
    return Stock(**stock_dict) 