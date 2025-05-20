# System Architecture

This document provides a visual representation and explanation of the Financial Screener application's architecture.

## Architecture Overview

The Financial Screener is a full-stack application built with a clear separation of concerns using a modern microservices-inspired architecture. The system is designed to be scalable, maintainable, and provide real-time data processing capabilities.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         CLIENT (Web Browser)                            │
└───────────────────────────────────┬─────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                              FRONTEND                                   │
│                                                                         │
│  ┌─────────────┐    ┌──────────────┐    ┌────────────┐   ┌───────────┐  │
│  │    React    │◄──►│  React Router│◄───►│  Zustand  │   │ Chart.js  │  │
│  └─────────────┘    └──────────────┘    └────────────┘   └───────────┘  │
│         │                   │                 │               │          │
│         └───────────────────┴─────────────────┴───────────────┘          │
│                                    │                                     │
│                                    │                                     │
│  ┌──────────────────────┐  ┌───────▼───────┐  ┌──────────────────────┐  │
│  │    Auth Service      │  │   API Client  │  │   Data Processing    │  │
│  │    (JWT Handler)     │◄─►│    (Axios)   │◄─►│     & Caching       │  │
│  └──────────────────────┘  └───────────────┘  └──────────────────────┘  │
│                                    │                                     │
└────────────────────────────────────┼─────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         API GATEWAY (FastAPI)                           │
│                                                                         │
│  ┌──────────────────────┐  ┌───────────────┐  ┌──────────────────────┐  │
│  │   Authentication     │  │   Rate        │  │    Request           │  │
│  │   Middleware        │  │   Limiting     │  │    Validation        │  │
│  └──────────────────────┘  └───────────────┘  └──────────────────────┘  │
│                                                                         │
└────────────────────────────────────┼─────────────────────────────────────┘
                                     │
                                     ▼
┌────────────────┬────────────────────┼────────────────────┬───────────────┐
│                │                    │                    │               │
▼                ▼                    ▼                    ▼               ▼
┌────────────┐ ┌────────────┐ ┌─────────────────┐ ┌─────────────┐ ┌───────────────┐
│  User      │ │  Stock     │ │  Screener       │ │  Portfolio  │ │  Backtesting  │
│  Service   │ │  Service   │ │  Service        │ │  Service    │ │  Service      │
└────────────┘ └────────────┘ └─────────────────┘ └─────────────┘ └───────────────┘
      │              │                │                 │                │
      ▼              ▼                ▼                 ▼                ▼
┌────────────┐ ┌────────────┐ ┌─────────────────┐ ┌─────────────┐ ┌───────────────┐
│  User      │ │  Stock     │ │  Screener       │ │  Portfolio  │ │  Backtesting  │
│  Data      │ │  Data      │ │  Data           │ │  Data       │ │  Data         │
└────────────┘ └────────────┘ └─────────────────┘ └─────────────┘ └───────────────┘
                     │
                     ▼
              ┌─────────────────┐
              │  External APIs  │
              │ (Alpha Vantage) │
              └─────────────────┘
```

## Component Details

### Frontend

1. **React Application**
   - Built with TypeScript for type safety
   - Uses Tailwind CSS for styling
   - Modular component architecture

2. **State Management**
   - Zustand for global state management
   - React Query for server state and data fetching
   - Local component state where appropriate

3. **Routing**
   - React Router for client-side routing
   - Protected routes for authenticated sections

4. **API Client**
   - Axios for HTTP requests
   - Centralized API service layer
   - Request/response interceptors for auth tokens

5. **Data Visualization**
   - Chart.js for rendering interactive charts
   - Custom dashboard components

### Backend

1. **API Gateway**
   - FastAPI framework
   - Handles routing to appropriate services
   - Authentication middleware
   - Request validation
   - Rate limiting
   - CORS configuration

2. **Services**
   - User Service: Authentication, user management
   - Stock Service: Stock data retrieval and caching
   - Screener Service: Stock filtering and screening logic
   - Portfolio Service: Portfolio management and performance tracking
   - Backtesting Service: Strategy testing against historical data

3. **Database**
   - MongoDB for flexible schema design
   - Efficient document-based storage for financial data
   - Indexing for optimized query performance

4. **External Integrations**
   - Alpha Vantage API for financial data
   - WebSockets for real-time updates

## Data Flow

1. **Authentication Flow**
   ```
   Client → Login Request → API Gateway → User Service → 
   Database (Verify) → JWT Created → Client (Store Token)
   ```

2. **Stock Data Flow**
   ```
   Client → Stock Data Request → API Gateway → Stock Service → 
   Check Cache → [If Not Cached] External API → 
   Process Data → Store in DB → Return to Client
   ```

3. **Screener Flow**
   ```
   Client → Screen Request (Filters) → API Gateway → Screener Service → 
   Query Database → Apply Filters → Return Filtered Stocks → Client
   ```

4. **Portfolio/Trading Flow**
   ```
   Client → Execute Trade → API Gateway → Portfolio Service → 
   Validate Trade → Update Portfolio → Return Updated Status → 
   WebSocket Update → Client (Real-time Update)
   ```

5. **Backtesting Flow**
   ```
   Client → Backtest Request → API Gateway → Backtesting Service → 
   Queue Job → Process Historical Data → Apply Strategy → 
   Calculate Performance → Store Results → Notify Completion → Client
   ```

## Deployment Architecture

```
┌───────────────────────────────────────┐
│             Load Balancer             │
└───────────────────────┬───────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
┌───────▼────┐   ┌──────▼─────┐   ┌─────▼──────┐
│  Frontend  │   │  Frontend  │   │  Frontend  │
│  Instance  │   │  Instance  │   │  Instance  │
└────────────┘   └────────────┘   └────────────┘
        │               │               │
        └───────────────┼───────────────┘
                        │
┌───────────────────────┼───────────────────────┐
│           API Gateway Load Balancer           │
└───────────────────────┬───────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
┌───────▼────┐   ┌──────▼─────┐   ┌─────▼──────┐
│  Backend   │   │  Backend   │   │  Backend   │
│  Instance  │   │  Instance  │   │  Instance  │
└────────────┘   └────────────┘   └────────────┘
        │               │               │
        └───────────────┼───────────────┘
                        │
                        ▼
              ┌─────────────────┐
              │                 │
              │    MongoDB      │
              │                 │
              └─────────────────┘
```

## Scaling Considerations

The Financial Screener architecture is designed with scalability in mind:

1. **Horizontal Scaling**
   - Stateless services can be scaled horizontally
   - Load balancers distribute traffic appropriately

2. **Database Scaling**
   - MongoDB sharding for handling large datasets
   - Read replicas for distributing read operations

3. **Caching Layer**
   - Caching of frequently accessed financial data
   - Reduces load on external API services

4. **Asynchronous Processing**
   - Long-running operations (like backtesting) run asynchronously
   - Job queues manage processing load

## Security Considerations

1. **Authentication and Authorization**
   - JWT-based authentication
   - Role-based access control
   - Token expiration and refresh mechanism

2. **Data Protection**
   - HTTPS for all communications
   - Password hashing using bcrypt
   - Input validation and sanitization

3. **API Security**
   - Rate limiting to prevent abuse
   - CORS policies to prevent unauthorized access
   - Request validation

4. **Infrastructure Security**
   - Firewall rules
   - Regular security updates
   - Principle of least privilege for services

## Monitoring and Observability

1. **Logging**
   - Centralized logging system
   - Application and access logs
   - Error tracking

2. **Metrics**
   - Service performance metrics
   - Database query metrics
   - External API call metrics

3. **Alerting**
   - Automated alerts for system issues
   - API availability monitoring
   - Database performance monitoring 