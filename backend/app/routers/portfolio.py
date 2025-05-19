from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.models.portfolio import Portfolio, PortfolioCreate
from app.db.mongodb import get_database

router = APIRouter()

@router.get("/", response_model=List[Portfolio])
async def get_portfolios():
    db = await get_database()
    portfolios = await db.portfolios.find().to_list(length=100)
    return portfolios

@router.post("/", response_model=Portfolio)
async def create_portfolio(portfolio: PortfolioCreate):
    db = await get_database()
    portfolio_dict = portfolio.dict()
    result = await db.portfolios.insert_one(portfolio_dict)
    portfolio_dict["id"] = str(result.inserted_id)
    return Portfolio(**portfolio_dict) 