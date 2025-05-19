# Financial Screener

A full-stack financial stock screener and paper trading platform inspired by screener.in and similar platforms.

## Features

- **Stock Screening**: Filter and search for stocks based on various financial metrics
- **Paper Trading**: Practice trading with virtual capital
- **Portfolio Management**: Track performance of your investments
- **Backtesting**: Test trading strategies against historical data
- **Interactive Charts**: Visualize stock price movements and financial data
- **Custom Saved Screens**: Save and reuse your screening criteria
- **Pre-defined Strategies**: Apply popular investing strategies with one click

## Technology Stack

### Backend
- Python
- FastAPI
- MongoDB
- Alpha Vantage API for financial data

### Frontend
- React
- TypeScript
- Tailwind CSS
- React Query for data fetching
- Zustand for state management
- Chart.js for data visualization

## Installation

### Prerequisites
- Node.js (v14+)
- Python (v3.8+)
- MongoDB

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

## Usage

1. Start both backend and frontend servers
2. Register an account or login with demo credentials
3. Explore stocks using the screener
4. Create and save custom screens
5. Execute paper trades
6. Track portfolio performance
7. Backtest trading strategies

## Contributing

Contributions are welcome! Feel free to submit a pull request.

## License

MIT License

## Acknowledgments

- Inspired by [screener.in](https://www.screener.in)
- Financial data provided by Alpha Vantage API 