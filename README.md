# Financial Screener

A full-stack financial stock screener and paper trading platform inspired by screener.in and similar platforms. This application allows users to analyze stocks, practice trading strategies with virtual money, and manage investment portfolios using real-time financial data.

## Features

- **Stock Screening**: Filter and search for stocks based on various financial metrics (P/E ratio, EPS, market cap, etc.)
- **Paper Trading**: Practice trading with virtual capital without risking real money
- **Portfolio Management**: Track performance of your investments with detailed metrics and visualizations
- **Backtesting**: Test trading strategies against historical data to validate investment approaches
- **Interactive Charts**: Visualize stock price movements and financial data with customizable timeframes
- **Custom Saved Screens**: Save and reuse your screening criteria for consistent analysis
- **Pre-defined Strategies**: Apply popular investing strategies (Value, Growth, Dividend, etc.) with one click
- **Watchlists**: Create and manage lists of stocks you're interested in tracking
- **Alerts**: Set up notifications for price movements or financial metric thresholds

## Technology Stack

### Backend
- **Python**: Core programming language for backend development
- **FastAPI**: High-performance web framework for building APIs
- **MongoDB**: NoSQL database for flexible data storage
- **Alpha Vantage API**: Primary source for financial data
- **JWT**: Token-based authentication system
- **Bcrypt**: Password hashing for secure user authentication
- **Pandas**: Data manipulation and analysis
- **Pytest**: Testing framework

### Frontend
- **React**: JavaScript library for building the user interface
- **TypeScript**: Type-safe JavaScript for improved developer experience
- **Tailwind CSS**: Utility-first CSS framework for styling
- **React Query**: Data fetching and caching library
- **Zustand**: State management solution
- **Chart.js**: Library for creating interactive charts
- **React Router**: Navigation and routing
- **Axios**: HTTP client for API requests

## Project Structure

```
financial-screener/
├── frontend/                # React frontend application
│   ├── public/              # Static files
│   │   ├── components/      # Reusable UI components
│   │   ├── pages/           # Application pages
│   │   ├── stores/          # State management
│   │   ├── services/        # API services
│   │   └── utils/           # Utility functions
│   ├── package.json         # Dependencies and scripts
│   └── tsconfig.json        # TypeScript configuration
│
├── backend/                 # FastAPI backend application
│   ├── app/                 # Application code
│   │   ├── api/             # API endpoints
│   │   ├── core/            # Core functionality
│   │   ├── db/              # Database models and connections
│   │   ├── services/        # Business logic services
│   │   └── utils/           # Utility functions
│   ├── tests/               # Test suite
│   ├── requirements.txt     # Python dependencies
│   └── main.py              # Application entry point
│
├── docs/                    # Documentation
│   ├── API_DOCUMENTATION.md # API reference
│   ├── ARCHITECTURE.md      # System architecture
│   └── TECHNOLOGY_CHOICES.md # Technology decisions
│
└── README.md                # Project overview
```

## Installation

### Prerequisites
- Node.js (v16+)
- Python (v3.9+)
- MongoDB (v4.4+)
- Git

### Environment Setup

1. Clone the repository
```bash
git clone https://github.com/yourusername/financial-screener.git
cd financial-screener
```

2. Create environment files

Create `.env` files in both frontend and backend directories:

Backend `.env`:
```
MONGODB_URI=mongodb://localhost:27017/financial_screener
ALPHA_VANTAGE_API_KEY=your_api_key_here
JWT_SECRET=your_jwt_secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

Frontend `.env`:
```
REACT_APP_API_URL=http://localhost:8000
```

### Backend Setup
```bash
cd backend
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

## Development

### Running Tests
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### API Documentation
After starting the backend server, access the auto-generated Swagger UI documentation at:
```
http://localhost:8000/docs
```

For detailed API documentation, see [API_DOCUMENTATION.md](./docs/API_DOCUMENTATION.md).

## Usage

1. Start both backend and frontend servers following the installation instructions
2. Register an account or login with demo credentials (if available)
3. Explore stocks using the screener with various financial filters
4. Create and save custom screens for repeated analysis
5. Execute paper trades to practice investment strategies
6. Track portfolio performance with detailed metrics
7. Backtest trading strategies against historical data
8. Set up alerts for price movements or financial thresholds

## System Architecture

For a visual representation of the system architecture, see [ARCHITECTURE.md](./docs/ARCHITECTURE.md).

## Technology Choices

For detailed explanations of technology decisions, see [TECHNOLOGY_CHOICES.md](./docs/TECHNOLOGY_CHOICES.md).

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License

## Acknowledgments

- Inspired by [screener.in](https://www.screener.in)
- Financial data provided by [Alpha Vantage API](https://www.alphavantage.co/)
- Icons from [Heroicons](https://heroicons.com/) 