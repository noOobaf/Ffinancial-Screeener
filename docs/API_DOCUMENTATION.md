# API Documentation

This document provides detailed information on the Financial Screener API endpoints, request/response formats, authentication requirements, and testing procedures.

## Base URL

All API endpoints are relative to:

```
http://localhost:8000
```

For production environments, the base URL will differ based on your deployment configuration.

## Authentication

The API uses JWT (JSON Web Token) based authentication. Most endpoints require a valid JWT token to be included in the request headers.

### Authentication Header

```
Authorization: Bearer <token>
```

### Authentication Endpoints

#### Register a new user

```
POST /api/users/register
```

Request body:
```json
{
  "email": "user@example.com",
  "password": "securepassword",
  "full_name": "John Doe"
}
```

Response (201 Created):
```json
{
  "id": "user_id",
  "email": "user@example.com",
  "full_name": "John Doe"
}
```

#### Login

```
POST /api/users/login
```

Request body:
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

Response (200 OK):
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user": {
    "id": "user_id",
    "email": "user@example.com",
    "full_name": "John Doe"
  }
}
```

## User Endpoints

### Get Current User

```
GET /api/users/me
```

Response (200 OK):
```json
{
  "id": "user_id",
  "email": "user@example.com",
  "full_name": "John Doe",
  "created_at": "2023-01-01T00:00:00Z"
}
```

### Update User

```
PUT /api/users/me
```

Request body:
```json
{
  "full_name": "John Smith",
  "password": "newsecurepassword"
}
```

Response (200 OK):
```json
{
  "id": "user_id",
  "email": "user@example.com",
  "full_name": "John Smith",
  "updated_at": "2023-01-02T00:00:00Z"
}
```

## Stock Data Endpoints

### Search Stocks

```
GET /api/stocks/search?query={query}
```

Response (200 OK):
```json
{
  "results": [
    {
      "symbol": "AAPL",
      "name": "Apple Inc.",
      "type": "Equity",
      "exchange": "NASDAQ"
    },
    {
      "symbol": "AMZN",
      "name": "Amazon.com Inc.",
      "type": "Equity",
      "exchange": "NASDAQ"
    }
  ]
}
```

### Get Stock Details

```
GET /api/stocks/{symbol}
```

Response (200 OK):
```json
{
  "symbol": "AAPL",
  "name": "Apple Inc.",
  "exchange": "NASDAQ",
  "sector": "Technology",
  "industry": "Consumer Electronics",
  "current_price": 150.25,
  "market_cap": 2500000000000,
  "pe_ratio": 25.6,
  "dividend_yield": 0.58,
  "eps": 5.89,
  "52_week_high": 180.75,
  "52_week_low": 120.25
}
```

### Get Stock Price History

```
GET /api/stocks/{symbol}/history?period={period}
```

Parameters:
- period: "1d", "1w", "1m", "3m", "1y", "5y" (default: "1m")

Response (200 OK):
```json
{
  "symbol": "AAPL",
  "period": "1m",
  "data": [
    {
      "date": "2023-01-01",
      "open": 142.5,
      "high": 145.2,
      "low": 141.8,
      "close": 144.3,
      "volume": 75482156
    },
    // Additional data points...
  ]
}
```

## Screener Endpoints

### Screen Stocks

```
POST /api/screener/screen
```

Request body:
```json
{
  "filters": {
    "market_cap": {
      "min": 1000000000,
      "max": 100000000000
    },
    "pe_ratio": {
      "min": 5,
      "max": 25
    },
    "sector": ["Technology", "Healthcare"],
    "dividend_yield": {
      "min": 1.5
    }
  },
  "sort_by": "market_cap",
  "sort_direction": "desc",
  "limit": 20,
  "offset": 0
}
```

Response (200 OK):
```json
{
  "results": [
    {
      "symbol": "MSFT",
      "name": "Microsoft Corporation",
      "current_price": 280.15,
      "market_cap": 2100000000000,
      "pe_ratio": 22.5,
      "dividend_yield": 1.75,
      "sector": "Technology"
    },
    // Additional results...
  ],
  "total": 87,
  "page": 1,
  "pages": 5
}
```

### Save Screen

```
POST /api/screener/saved
```

Request body:
```json
{
  "name": "My Value Stocks",
  "description": "Low PE ratio tech stocks with dividends",
  "filters": {
    "market_cap": {
      "min": 1000000000,
      "max": 100000000000
    },
    "pe_ratio": {
      "min": 5,
      "max": 25
    },
    "sector": ["Technology"],
    "dividend_yield": {
      "min": 1.5
    }
  },
  "sort_by": "market_cap",
  "sort_direction": "desc"
}
```

Response (201 Created):
```json
{
  "id": "screen_id",
  "name": "My Value Stocks",
  "description": "Low PE ratio tech stocks with dividends",
  "filters": {
    // Filters data
  },
  "created_at": "2023-01-01T00:00:00Z"
}
```

### Get Saved Screens

```
GET /api/screener/saved
```

Response (200 OK):
```json
{
  "screens": [
    {
      "id": "screen_id",
      "name": "My Value Stocks",
      "description": "Low PE ratio tech stocks with dividends",
      "created_at": "2023-01-01T00:00:00Z"
    },
    // Additional screens...
  ]
}
```

### Get Saved Screen by ID

```
GET /api/screener/saved/{screen_id}
```

Response (200 OK):
```json
{
  "id": "screen_id",
  "name": "My Value Stocks",
  "description": "Low PE ratio tech stocks with dividends",
  "filters": {
    // Filters data
  },
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z"
}
```

### Delete Saved Screen

```
DELETE /api/screener/saved/{screen_id}
```

Response (204 No Content)

## Portfolio Endpoints

### Create Portfolio

```
POST /api/portfolios
```

Request body:
```json
{
  "name": "My Growth Portfolio",
  "description": "Portfolio focused on growth stocks",
  "initial_balance": 100000
}
```

Response (201 Created):
```json
{
  "id": "portfolio_id",
  "name": "My Growth Portfolio",
  "description": "Portfolio focused on growth stocks",
  "initial_balance": 100000,
  "current_balance": 100000,
  "created_at": "2023-01-01T00:00:00Z"
}
```

### Get User Portfolios

```
GET /api/portfolios
```

Response (200 OK):
```json
{
  "portfolios": [
    {
      "id": "portfolio_id",
      "name": "My Growth Portfolio",
      "description": "Portfolio focused on growth stocks",
      "initial_balance": 100000,
      "current_balance": 105250.75,
      "created_at": "2023-01-01T00:00:00Z"
    },
    // Additional portfolios...
  ]
}
```

### Get Portfolio Details

```
GET /api/portfolios/{portfolio_id}
```

Response (200 OK):
```json
{
  "id": "portfolio_id",
  "name": "My Growth Portfolio",
  "description": "Portfolio focused on growth stocks",
  "initial_balance": 100000,
  "current_balance": 105250.75,
  "cash_balance": 25250.75,
  "total_value": 105250.75,
  "performance": {
    "absolute": 5250.75,
    "percentage": 5.25
  },
  "holdings": [
    {
      "symbol": "AAPL",
      "name": "Apple Inc.",
      "shares": 50,
      "average_price": 150.00,
      "current_price": 160.00,
      "market_value": 8000.00,
      "profit_loss": 500.00,
      "profit_loss_percent": 6.67,
      "allocation_percent": 7.6
    },
    // Additional holdings...
  ],
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-05T00:00:00Z"
}
```

### Delete Portfolio

```
DELETE /api/portfolios/{portfolio_id}
```

Response (204 No Content)

## Paper Trading Endpoints

### Execute Trade

```
POST /api/portfolios/{portfolio_id}/trades
```

Request body:
```json
{
  "symbol": "AAPL",
  "action": "buy",
  "shares": 10,
  "price": 150.25,
  "date": "2023-01-05T15:30:00Z"
}
```

Response (201 Created):
```json
{
  "id": "trade_id",
  "portfolio_id": "portfolio_id",
  "symbol": "AAPL",
  "action": "buy",
  "shares": 10,
  "price": 150.25,
  "total": 1502.50,
  "date": "2023-01-05T15:30:00Z",
  "status": "completed"
}
```

### Get Portfolio Trades

```
GET /api/portfolios/{portfolio_id}/trades
```

Response (200 OK):
```json
{
  "trades": [
    {
      "id": "trade_id",
      "portfolio_id": "portfolio_id",
      "symbol": "AAPL",
      "action": "buy",
      "shares": 10,
      "price": 150.25,
      "total": 1502.50,
      "date": "2023-01-05T15:30:00Z",
      "status": "completed"
    },
    // Additional trades...
  ]
}
```

## Backtesting Endpoints

### Create Backtest

```
POST /api/backtests
```

Request body:
```json
{
  "name": "Moving Average Crossover Strategy",
  "description": "Simple strategy based on 50-day and 200-day moving averages",
  "strategy": {
    "type": "moving_average_crossover",
    "parameters": {
      "fast_period": 50,
      "slow_period": 200
    }
  },
  "symbols": ["AAPL", "MSFT", "AMZN", "GOOGL"],
  "start_date": "2022-01-01",
  "end_date": "2022-12-31",
  "initial_capital": 100000
}
```

Response (202 Accepted):
```json
{
  "id": "backtest_id",
  "status": "pending",
  "name": "Moving Average Crossover Strategy",
  "created_at": "2023-01-10T00:00:00Z"
}
```

### Get Backtest Results

```
GET /api/backtests/{backtest_id}
```

Response (200 OK):
```json
{
  "id": "backtest_id",
  "name": "Moving Average Crossover Strategy",
  "description": "Simple strategy based on 50-day and 200-day moving averages",
  "status": "completed",
  "strategy": {
    "type": "moving_average_crossover",
    "parameters": {
      "fast_period": 50,
      "slow_period": 200
    }
  },
  "symbols": ["AAPL", "MSFT", "AMZN", "GOOGL"],
  "start_date": "2022-01-01",
  "end_date": "2022-12-31",
  "initial_capital": 100000,
  "final_capital": 112500.75,
  "return": 12.5,
  "max_drawdown": -8.2,
  "sharpe_ratio": 1.25,
  "trades": [
    {
      "symbol": "AAPL",
      "action": "buy",
      "date": "2022-02-15",
      "price": 145.25,
      "shares": 10,
      "total": 1452.50
    },
    // Additional trades...
  ],
  "equity_curve": [
    {
      "date": "2022-01-01",
      "equity": 100000
    },
    // Additional equity points...
  ],
  "created_at": "2023-01-10T00:00:00Z",
  "completed_at": "2023-01-10T00:15:32Z"
}
```

## Error Handling

The API uses standard HTTP status codes to indicate the success or failure of requests:

- 200 OK: The request was successful
- 201 Created: A resource was successfully created
- 202 Accepted: The request was accepted for processing
- 204 No Content: The request was successful but there is no content to return
- 400 Bad Request: The request was invalid or cannot be otherwise served
- 401 Unauthorized: Authentication is required or failed
- 403 Forbidden: The request is understood but refused due to permissions
- 404 Not Found: The requested resource does not exist
- 422 Unprocessable Entity: The request was well-formed but could not be processed
- 429 Too Many Requests: Rate limit exceeded
- 500 Internal Server Error: Something went wrong on the server

### Error Response Format

```json
{
  "error": {
    "code": "error_code",
    "message": "A human-readable error message",
    "details": {
      // Additional error details if available
    }
  }
}
```

## Rate Limiting

The API implements rate limiting to protect against abuse. The current limits are:

- 100 requests per minute for authenticated users
- 20 requests per minute for unauthenticated users

Rate limit information is included in the response headers:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

## Testing the API

### Using Swagger UI

The API provides a Swagger UI interface for testing endpoints interactively. Access it at:

```
http://localhost:8000/docs
```

### Using curl

Example of authenticating and making a request:

```bash
# Login to get a token
TOKEN=$(curl -s -X POST http://localhost:8000/api/users/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"securepassword"}' \
  | jq -r .access_token)

# Use the token to make an authenticated request
curl -X GET http://localhost:8000/api/users/me \
  -H "Authorization: Bearer $TOKEN"
```

### Using Postman

1. Download and install [Postman](https://www.postman.com/downloads/)
2. Import the provided [Postman collection](https://example.com/financial-screener-api.postman_collection.json)
3. Set up an environment with your base URL and authentication credentials
4. Run the login request first to obtain an authentication token
5. Other requests will use this token automatically via Postman environment variables

## WebSocket API

The API also provides WebSocket endpoints for real-time data:

### Stock Price Updates

```
ws://localhost:8000/ws/stocks/{symbol}
```

Example message:
```json
{
  "symbol": "AAPL",
  "price": 150.25,
  "change": 0.75,
  "change_percent": 0.5,
  "timestamp": "2023-01-05T15:30:00Z"
}
```

### Portfolio Updates

```
ws://localhost:8000/ws/portfolios/{portfolio_id}
```

Example message:
```json
{
  "portfolio_id": "portfolio_id",
  "current_balance": 105250.75,
  "total_value": 105250.75,
  "performance": {
    "absolute": 5250.75,
    "percentage": 5.25
  },
  "timestamp": "2023-01-05T15:30:00Z"
}
``` 