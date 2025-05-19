from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.models.screener import Screener, ScreenerCreate
from app.db.mongodb import get_database

router = APIRouter()

@router.get("/", response_model=List[Screener])
async def get_screeners():
    db = await get_database()
    screeners = await db.screeners.find().to_list(length=100)
    return screeners

@router.post("/", response_model=Screener)
async def create_screener(screener: ScreenerCreate):
    db = await get_database()
    screener_dict = screener.dict()
    result = await db.screeners.insert_one(screener_dict)
    screener_dict["id"] = str(result.inserted_id)
    return Screener(**screener_dict) 