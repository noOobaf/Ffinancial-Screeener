import aiohttp
from typing import Optional, Dict, Any
from app.core.config import settings

class AlphaVantageAPI:
    BASE_URL = "https://www.alphavantage.co/query"
    
    def __init__(self):
        self.api_key = settings.ALPHA_VANTAGE_API_KEY
    
    async def _make_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        params["apikey"] = self.api_key
        async with aiohttp.ClientSession() as session:
            async with session.get(self.BASE_URL, params=params) as response:
                return await response.json()
    
    async def get_quote(self, symbol: str) -> Dict[str, Any]:
        """Get real-time quote for a symbol"""
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol
        }
        return await self._make_request(params)
    
    async def get_company_overview(self, symbol: str) -> Dict[str, Any]:
        """Get company overview and financial metrics"""
        params = {
            "function": "OVERVIEW",
            "symbol": symbol
        }
        return await self._make_request(params)
    
    async def get_income_statement(self, symbol: str) -> Dict[str, Any]:
        """Get annual income statements"""
        params = {
            "function": "INCOME_STATEMENT",
            "symbol": symbol
        }
        return await self._make_request(params)
    
    async def get_balance_sheet(self, symbol: str) -> Dict[str, Any]:
        """Get annual balance sheets"""
        params = {
            "function": "BALANCE_SHEET",
            "symbol": symbol
        }
        return await self._make_request(params)
    
    async def get_cash_flow(self, symbol: str) -> Dict[str, Any]:
        """Get annual cash flow statements"""
        params = {
            "function": "CASH_FLOW",
            "symbol": symbol
        }
        return await self._make_request(params)
    
    async def get_daily_adjusted(self, symbol: str, outputsize: str = "compact") -> Dict[str, Any]:
        """Get daily adjusted time series"""
        params = {
            "function": "TIME_SERIES_DAILY_ADJUSTED",
            "symbol": symbol,
            "outputsize": outputsize
        }
        return await self._make_request(params)
    
    async def search_symbols(self, keywords: str) -> Dict[str, Any]:
        """Search for symbols matching keywords"""
        params = {
            "function": "SYMBOL_SEARCH",
            "keywords": keywords
        }
        return await self._make_request(params)

alpha_vantage = AlphaVantageAPI() 