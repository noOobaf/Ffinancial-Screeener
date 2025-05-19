from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
import jwt
from datetime import datetime, timedelta
import requests
import json
import random
import os
from typing import List, Optional, Dict, Any
from fastapi.responses import JSONResponse
# Comment out MongoDB connection for now
# from app.routers import auth, portfolio, stocks, screeners
# from app.db.mongodb import connect_to_mongo, close_mongo_connection

# Define Pydantic models for users
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class Trade(BaseModel):
    symbol: str
    shares: int
    type: str
    price: float

class FinancialData(BaseModel):
    revenue: float
    netIncome: float
    eps: float
    dividend: float
    dividendYield: float

class HistoricalPrice(BaseModel):
    date: str
    price: float

class StockData(BaseModel):
    symbol: str
    companyName: str
    currentPrice: float
    change: float
    changePercent: float
    marketCap: float
    peRatio: float
    volume: int
    historicalPrices: List[HistoricalPrice]

# Define an improved UserLogin model with validation
class UserLoginFixed(BaseModel):
    username: str
    password: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "user",
                "password": "password"
            }
        }

# Add this near the top with other models
class BacktestStrategy(BaseModel):
    name: str
    description: str
    signals: List[str]
    parameters: Dict[str, Any]

class BacktestRequest(BaseModel):
    strategy_id: Optional[str] = None
    strategy: Optional[BacktestStrategy] = None
    symbol: str
    start_date: str
    end_date: str
    initial_capital: float = 10000.0
    position_size: float = 0.1  # 10% of capital per trade

class BacktestResult(BaseModel):
    strategy_name: str
    symbol: str
    start_date: str
    end_date: str
    initial_capital: float
    final_capital: float
    total_return: float
    annualized_return: float
    max_drawdown: float
    win_rate: float
    trades: List[dict]
    equity_curve: List[dict]

SECRET_KEY = "your-secure-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI(
    title="Financial Screener API",
    description="API for financial screening and paper trading platform",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React app URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers - commented out for now
# app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
# app.include_router(portfolio.router, prefix="/api/v1/portfolio", tags=["portfolio"])
# app.include_router(stocks.router, prefix="/api/v1/stocks", tags=["stocks"])
# app.include_router(screeners.router, prefix="/api/v1/screeners", tags=["screeners"])

# Comment out DB connection events
# @app.on_event("startup")
# async def startup_db_client():
#     await connect_to_mongo()

# @app.on_event("shutdown")
# async def shutdown_db_client():
#     await close_mongo_connection()

# In-memory user storage for testing
fake_users_db = {
    "testuser": {
        "username": "testuser",
        "email": "test@example.com",
        "hashed_password": "fakehashedpassword",
    },
    "user": {
        "username": "user",
        "email": "user@example.com",
        "hashed_password": "password",
    }
}

# In-memory storage for demo purposes
portfolio_db = {}
trades_db = []

# Helper functions for fetching stock data
def fetch_stock_data(symbol: str) -> dict:
    """Fetch real stock data from a public API"""
    try:
        # For demo purposes, we'll generate random data
        # In a real app, you would use a proper API like Alpha Vantage, IEX Cloud, etc.
        current_price = round(random.uniform(50, 500), 2)
        change = round(random.uniform(-20, 20), 2)
        change_percent = round((change / (current_price - change)) * 100, 2)
        
        # Generate random historical data for past 6 months
        historical_prices = []
        base_price = current_price - change  # Starting price
        for i in range(6):
            month = 5 - i  # Going backwards from current month
            # Create a realistic price trajectory
            price = round(base_price * (1 + random.uniform(-0.15, 0.15)), 2)
            date = f"2025-{month+1:02d}-01"  # Format: YYYY-MM-DD
            historical_prices.append({"date": date, "price": price})
            base_price = price
        
        # Sort historical prices by date (oldest first)
        historical_prices.sort(key=lambda x: x["date"])
        
        return {
            "symbol": symbol,
            "companyName": f"{symbol} Inc.",
            "currentPrice": current_price,
            "change": change,
            "changePercent": change_percent,
            "marketCap": round(current_price * random.randint(1000000, 10000000000)),
            "peRatio": round(random.uniform(10, 50), 2),
            "volume": random.randint(1000000, 100000000),
            "historicalPrices": historical_prices
        }
    except Exception as e:
        print(f"Error fetching stock data: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching stock data: {str(e)}")

def fetch_financial_data(symbol: str) -> dict:
    """Fetch financial data for a stock"""
    try:
        # For demo purposes, we'll generate random data
        current_price = fetch_stock_data(symbol)["currentPrice"]
        revenue = round(random.uniform(1000000000, 500000000000), 2)
        net_income = round(revenue * random.uniform(0.05, 0.25), 2)
        eps = round(net_income / random.randint(100000000, 5000000000), 2)
        dividend = round(current_price * random.uniform(0.005, 0.05), 2)
        dividend_yield = round((dividend / current_price) * 100, 2)
        
        return {
            "revenue": revenue,
            "netIncome": net_income,
            "eps": eps,
            "dividend": dividend,
            "dividendYield": dividend_yield
        }
    except Exception as e:
        print(f"Error fetching financial data: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching financial data: {str(e)}")

def generate_screener_results() -> List[dict]:
    """Generate screener results with randomly selected stocks"""
    symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "NVDA", "JPM", "V", "WMT"]
    results = []
    
    for symbol in random.sample(symbols, min(len(symbols), 5)):
        stock_data = fetch_stock_data(symbol)
        results.append({
            "symbol": stock_data["symbol"],
            "companyName": stock_data["companyName"],
            "currentPrice": stock_data["currentPrice"],
            "change": stock_data["change"],
            "changePercent": stock_data["changePercent"],
            "marketCap": stock_data["marketCap"],
            "peRatio": stock_data["peRatio"],
            "volume": stock_data["volume"]
        })
    
    return results

# Helper functions for authentication
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@app.get("/")
async def root():
    return {
        "message": "Welcome to Financial Screener API",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }

# Auth endpoints
@app.post("/api/v1/auth/register", response_model=Token)
async def register_user(user: UserCreate):
    if user.username in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # In a real application, we would hash the password and store in a database
    fake_users_db[user.username] = {
        "username": user.username,
        "email": user.email,
        "hashed_password": user.password,  # This would be hashed in a real application
    }
    
    # Initialize empty portfolio for new user
    portfolio_db[user.username] = []
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/api/v1/auth/login", response_model=Token)
async def login_for_access_token(user: UserLogin, request: Request):
    print(f"Login attempt for user: {user.username}")
    
    # Debug: print request body
    body = await request.body()
    print(f"Raw request body: {body}")
    
    # Debug: print the user object
    print(f"UserLogin object: {user}")
    print(f"Checking against fake_users_db: {fake_users_db}")
    
    # Simple validation - in a real app this would check hashed passwords
    if user.username not in fake_users_db:
        print(f"User not found: {user.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if fake_users_db[user.username]["hashed_password"] != user.password:
        print(f"Invalid password for user: {user.username}")
        print(f"Expected: {fake_users_db[user.username]['hashed_password']}, Got: {user.password}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    print(f"Login successful for {user.username}, token: {access_token}")
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/api/v1/auth/login-form")
async def login_with_form(form_data: OAuth2PasswordRequestForm = Depends()):
    print(f"Form login attempt for user: {form_data.username}")
    
    if form_data.username not in fake_users_db:
        print(f"User not found: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if fake_users_db[form_data.username]["hashed_password"] != form_data.password:
        print(f"Invalid password for user: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": form_data.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/v1/auth/me")
async def get_current_user():
    return {"username": "testuser", "email": "test@example.com"}

@app.get("/api/v1/portfolio/holdings")
async def get_holdings():
    # In a real app, you would get the user from the token and return their holdings
    holdings = []
    
    # Generate some sample holdings
    symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
    for symbol in random.sample(symbols, min(len(symbols), 3)):
        stock_data = fetch_stock_data(symbol)
        current_price = stock_data["currentPrice"]
        shares = random.randint(1, 20)
        avg_price = round(current_price * (1 + random.uniform(-0.2, 0.1)), 2)
        market_value = round(shares * current_price, 2)
        unrealized_pl = round(market_value - (shares * avg_price), 2)
        
        holdings.append({
            "symbol": symbol,
            "shares": shares,
            "avgPrice": avg_price,
            "currentPrice": current_price,
            "marketValue": market_value,
            "unrealizedPL": unrealized_pl
        })
    
    return holdings

@app.post("/api/v1/portfolio/trade")
async def execute_trade(trade: Trade):
    # In a real app, you would get the user from the token and update their portfolio
    trade_id = f"trade_{len(trades_db) + 1}"
    timestamp = datetime.utcnow().isoformat()
    total = trade.shares * trade.price
    
    trade_record = {
        "id": trade_id,
        "symbol": trade.symbol,
        "shares": trade.shares,
        "price": trade.price,
        "type": trade.type,
        "timestamp": timestamp,
        "total": total
    }
    
    trades_db.append(trade_record)
    
    return {
        "success": True,
        "message": f"Successfully {trade.type}ed {trade.shares} shares of {trade.symbol}",
        "transaction": trade_record
    }

@app.get("/api/v1/portfolio/trades")
async def get_trades():
    # In a real app, you would get the user from the token and return their trades
    if not trades_db:
        # Generate some sample trades if none exist
        symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
        for i in range(5):
            symbol = random.choice(symbols)
            stock_data = fetch_stock_data(symbol)
            price = stock_data["currentPrice"]
            shares = random.randint(1, 20)
            trade_type = random.choice(["buy", "sell"])
            timestamp = (datetime.utcnow() - timedelta(days=random.randint(0, 30))).isoformat()
            
            trades_db.append({
                "id": f"trade_{i+1}",
                "symbol": symbol,
                "shares": shares,
                "price": price,
                "type": trade_type,
                "timestamp": timestamp,
                "total": round(shares * price, 2)
            })
    
    # Sort trades by timestamp (newest first)
    sorted_trades = sorted(trades_db, key=lambda x: x["timestamp"], reverse=True)
    
    return sorted_trades

@app.get("/api/v1/portfolio/performance")
async def get_performance():
    # In a real app, you would get the user from the token and return their performance
    days = 180  # 6 months
    values = []
    
    # Generate a somewhat realistic portfolio growth curve
    base_value = 10000  # Starting value
    current_value = base_value
    
    for i in range(days):
        # Add a small random change each day
        daily_change = random.uniform(-0.02, 0.025)  # -2% to +2.5%
        current_value = max(100, current_value * (1 + daily_change))  # Ensure we don't go below $100
        
        # Only add data points for the first of each month for simplicity
        if i % 30 == 0:
            date = (datetime.utcnow() - timedelta(days=days-i)).strftime("%Y-%m-%d")
            values.append({
                "date": date,
                "value": round(current_value, 2)
            })
    
    return values

@app.get("/api/v1/stocks/{symbol}")
async def get_stock(symbol: str):
    return fetch_stock_data(symbol)

@app.get("/api/v1/stocks/{symbol}/financials")
async def get_financials(symbol: str):
    return fetch_financial_data(symbol)

@app.get("/api/v1/screeners")
async def get_screeners():
    return [
        {"id": 1, "name": "High Growth", "description": "Companies with high growth potential", "rules": [
            {"metric": "peRatio", "operator": "<", "value": 30}
        ]},
        {"id": 2, "name": "Dividend Stocks", "description": "Stocks with good dividend yield", "rules": [
            {"metric": "dividendYield", "operator": ">", "value": 2.5}
        ]},
        {"id": 3, "name": "Large Cap Tech", "description": "Large tech companies", "rules": [
            {"metric": "marketCap", "operator": ">", "value": 1000000000000},
            {"metric": "sector", "operator": "=", "value": "Technology"}
        ]},
    ]

@app.get("/api/v1/screeners/results")
async def get_screener_results():
    return generate_screener_results()

# Update the login endpoint to use the fixed model
@app.post("/api/v1/auth/login-alt", response_model=Token)
async def login_alternative(user: UserLoginFixed):
    print(f"Alternative login attempt for user: {user.username}")
    
    # Simple validation
    if user.username not in fake_users_db:
        print(f"User not found: {user.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    
    if fake_users_db[user.username]["hashed_password"] != user.password:
        print(f"Invalid password for user: {user.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/api/v1/auth/login-raw")
async def login_raw(request: Request):
    try:
        # Get JSON directly from request
        data = await request.json()
        print(f"Raw login data: {data}")
        
        username = data.get("username")
        password = data.get("password")
        
        print(f"Raw login attempt for user: {username}")
        
        if not username or not password:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": "Missing username or password"}
            )
        
        if username not in fake_users_db:
            print(f"User not found: {username}")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Incorrect username or password"}
            )
        
        if fake_users_db[username]["hashed_password"] != password:
            print(f"Invalid password for user: {username}")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Incorrect username or password"}
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": username}, expires_delta=access_token_expires
        )
        
        print(f"Raw login successful for {username}")
        return {"access_token": access_token, "token_type": "bearer"}
    
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "Invalid JSON format"}
        )
    except Exception as e:
        print(f"Login error: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": f"Login error: {str(e)}"}
        )

@app.get("/api/v1/stocks/search")
async def search_stocks(q: str):
    """Search for stocks by symbol or company name"""
    # In a real app, this would search a database
    # For now, we'll use a small set of sample stocks
    sample_stocks = [
        {"symbol": "AAPL", "companyName": "Apple Inc."},
        {"symbol": "MSFT", "companyName": "Microsoft Corporation"},
        {"symbol": "GOOGL", "companyName": "Alphabet Inc."},
        {"symbol": "AMZN", "companyName": "Amazon.com Inc."},
        {"symbol": "META", "companyName": "Meta Platforms Inc."},
        {"symbol": "TSLA", "companyName": "Tesla Inc."},
        {"symbol": "NVDA", "companyName": "NVIDIA Corporation"},
        {"symbol": "JPM", "companyName": "JPMorgan Chase & Co."},
        {"symbol": "V", "companyName": "Visa Inc."},
        {"symbol": "WMT", "companyName": "Walmart Inc."},
        {"symbol": "JNJ", "companyName": "Johnson & Johnson"},
        {"symbol": "HD", "companyName": "Home Depot Inc."},
        {"symbol": "PG", "companyName": "Procter & Gamble Co."},
        {"symbol": "MA", "companyName": "Mastercard Inc."},
        {"symbol": "UNH", "companyName": "UnitedHealth Group Inc."}
    ]
    
    # Filter stocks based on the query
    q = q.lower()
    results = [
        stock for stock in sample_stocks
        if q in stock["symbol"].lower() or q in stock["companyName"].lower()
    ]
    
    return results[:10]  # Limit to 10 results

# Add this before the if __name__ block
@app.post("/api/v1/backtest", response_model=BacktestResult)
async def run_backtest(request: BacktestRequest):
    """Run a backtest for a given strategy and stock symbol"""
    try:
        stock_data = fetch_stock_data(request.symbol)
        
        # Generate historical data covering the backtest period
        # In a real implementation, you would fetch actual historical data
        # For this demo, we'll generate simulated price data
        start_date = datetime.strptime(request.start_date, "%Y-%m-%d")
        end_date = datetime.strptime(request.end_date, "%Y-%m-%d")
        
        # Generate daily prices for the period
        days_diff = (end_date - start_date).days
        if days_diff <= 0:
            raise HTTPException(status_code=400, detail="End date must be after start date")
        
        # Start with current price and work backwards with some randomness
        current_price = stock_data["currentPrice"]
        
        # Generate a somewhat realistic price series
        price_data = []
        price = current_price * (1 - random.uniform(0.1, 0.3))  # Start 10-30% lower than current
        
        # Generate dates and prices
        dates = []
        prices = []
        for i in range(days_diff + 1):
            day = start_date + timedelta(days=i)
            if day.weekday() < 5:  # Skip weekends
                price = price * (1 + random.uniform(-0.02, 0.025))  # Daily change between -2% and 2.5%
                dates.append(day.strftime("%Y-%m-%d"))
                prices.append(round(price, 2))
        
        # Simulate strategy execution
        capital = request.initial_capital
        position = 0  # Shares owned
        trades = []
        equity_curve = []
        
        # Simple moving average crossover strategy for demo
        # In a real implementation, this would be parameterized and more sophisticated
        short_window = 5
        long_window = 20
        
        # Calculate simple moving averages
        short_ma = []
        long_ma = []
        
        for i in range(len(prices)):
            if i >= short_window:
                short_ma.append(sum(prices[i-short_window:i]) / short_window)
            else:
                short_ma.append(None)
                
            if i >= long_window:
                long_ma.append(sum(prices[i-long_window:i]) / long_window)
            else:
                long_ma.append(None)
                
            equity = capital
            if position > 0:
                equity += position * prices[i]
            
            equity_curve.append({
                "date": dates[i],
                "equity": round(equity, 2),
                "price": prices[i]
            })
        
        # Execute trades based on moving average crossover
        for i in range(long_window, len(prices)):
            # Moving average crossover strategy
            if short_ma[i-1] is not None and long_ma[i-1] is not None:
                # Buy signal: short MA crosses above long MA
                if short_ma[i-1] <= long_ma[i-1] and short_ma[i] > long_ma[i]:
                    # Calculate position size
                    investment = capital * request.position_size
                    shares_to_buy = int(investment / prices[i])
                    
                    if shares_to_buy > 0:
                        cost = shares_to_buy * prices[i]
                        capital -= cost
                        position += shares_to_buy
                        
                        trades.append({
                            "date": dates[i],
                            "type": "buy",
                            "price": prices[i],
                            "shares": shares_to_buy,
                            "cost": round(cost, 2),
                            "capital": round(capital, 2)
                        })
                
                # Sell signal: short MA crosses below long MA
                elif short_ma[i-1] >= long_ma[i-1] and short_ma[i] < long_ma[i] and position > 0:
                    revenue = position * prices[i]
                    capital += revenue
                    
                    trades.append({
                        "date": dates[i],
                        "type": "sell",
                        "price": prices[i],
                        "shares": position,
                        "revenue": round(revenue, 2),
                        "capital": round(capital, 2)
                    })
                    
                    position = 0
        
        # Sell any remaining position at the end
        if position > 0:
            revenue = position * prices[-1]
            capital += revenue
            
            trades.append({
                "date": dates[-1],
                "type": "sell",
                "price": prices[-1],
                "shares": position,
                "revenue": round(revenue, 2),
                "capital": round(capital, 2)
            })
        
        # Calculate performance metrics
        final_capital = capital
        total_return = (final_capital / request.initial_capital - 1) * 100
        
        # Annualized return calculation
        years = days_diff / 365.0
        annualized_return = ((final_capital / request.initial_capital) ** (1/years) - 1) * 100 if years > 0 else 0
        
        # Calculate max drawdown
        peak = request.initial_capital
        max_drawdown = 0
        
        for point in equity_curve:
            equity = point["equity"]
            if equity > peak:
                peak = equity
            else:
                drawdown = (peak - equity) / peak * 100
                max_drawdown = max(max_drawdown, drawdown)
        
        # Calculate win rate
        wins = sum(1 for trade in trades if trade.get("type") == "sell" and 
                   trade.get("revenue", 0) > trade.get("cost", 0))
        total_trades = len([t for t in trades if t.get("type") == "sell"])
        win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
        
        return {
            "strategy_name": request.strategy.name if request.strategy else "Moving Average Crossover",
            "symbol": request.symbol,
            "start_date": request.start_date,
            "end_date": request.end_date,
            "initial_capital": request.initial_capital,
            "final_capital": round(final_capital, 2),
            "total_return": round(total_return, 2),
            "annualized_return": round(annualized_return, 2),
            "max_drawdown": round(max_drawdown, 2),
            "win_rate": round(win_rate, 2),
            "trades": trades,
            "equity_curve": equity_curve
        }
        
    except Exception as e:
        print(f"Backtest error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Backtest error: {str(e)}")

@app.get("/api/v1/backtest/strategies")
async def get_backtest_strategies():
    """Get available backtest strategies"""
    # In a real app, these would be fetched from a database
    return [
        {
            "id": "moving_avg_crossover",
            "name": "Moving Average Crossover",
            "description": "Buy when short MA crosses above long MA, sell when it crosses below",
            "parameters": {
                "short_window": {"type": "integer", "default": 5, "min": 2, "max": 50},
                "long_window": {"type": "integer", "default": 20, "min": 5, "max": 200}
            }
        },
        {
            "id": "rsi_strategy",
            "name": "RSI Strategy",
            "description": "Buy when RSI is below oversold level, sell when above overbought level",
            "parameters": {
                "rsi_period": {"type": "integer", "default": 14, "min": 2, "max": 30},
                "oversold": {"type": "integer", "default": 30, "min": 10, "max": 40},
                "overbought": {"type": "integer", "default": 70, "min": 60, "max": 90}
            }
        },
        {
            "id": "bollinger_bands",
            "name": "Bollinger Bands Strategy",
            "description": "Buy when price touches lower band, sell when it touches upper band",
            "parameters": {
                "window": {"type": "integer", "default": 20, "min": 5, "max": 50},
                "num_std": {"type": "number", "default": 2.0, "min": 1.0, "max": 3.0}
            }
        }
    ]

# Add this at the end of the file
if __name__ == "__main__":
    import uvicorn
    import sys
    
    port = 8000
    host = "127.0.0.1"
    
    # Display useful links in console before starting the server
    print("\n" + "="*50)
    print("\033[1m Financial Screener API Server \033[0m")
    print("="*50)
    print(f"\033[1m\033[94m API (root):     \033[0m http://{host}:{port}/")
    print(f"\033[1m\033[94m Swagger UI:     \033[0m http://{host}:{port}/docs")
    print(f"\033[1m\033[94m ReDoc:          \033[0m http://{host}:{port}/redoc")
    print(f"\033[1m\033[94m OpenAPI Schema: \033[0m http://{host}:{port}/openapi.json")
    print("="*50)
    print("\nPress Ctrl+C to quit\n")
    
    # Configure the server with the same settings used in the command
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,  # Enable auto-reload for development
        log_level="info"
    ) 