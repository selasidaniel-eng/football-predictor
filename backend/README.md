# Football Bet Predictor - Backend

FastAPI-based backend for the football match prediction system.

## Tech Stack

- **Framework:** FastAPI
- **Database:** PostgreSQL 14+
- **Cache:** Redis
- **ORM:** SQLAlchemy
- **ML:** scikit-learn, XGBoost
- **Scraping:** Playwright
- **Task Scheduler:** APScheduler
- **Authentication:** JWT + bcrypt

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Configuration management
│   ├── models/              # SQLAlchemy ORM models
│   ├── schemas/             # Pydantic request/response schemas
│   ├── api/
│   │   ├── __init__.py
│   │   ├── matches.py       # Match endpoints
│   │   ├── predictions.py   # Prediction endpoints
│   │   ├── users.py         # User endpoints
│   │   └── auth.py          # Authentication endpoints
│   ├── services/            # Business logic
│   │   ├── __init__.py
│   │   ├── prediction_service.py
│   │   ├── scraper_service.py
│   │   ├── ml_service.py
│   │   └── feature_engineering.py
│   ├── utils/               # Utility functions
│   │   ├── __init__.py
│   │   └── constants.py
│   └── tasks/               # Background tasks
│       ├── __init__.py
│       └── scheduler.py
├── tests/                   # Unit and integration tests
├── migrations/              # Alembic database migrations
├── requirements.txt         # Python dependencies
├── Dockerfile              # Container configuration
├── docker-compose.yml      # Local development stack
└── README.md              # This file
```

## Installation

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Redis 7+
- Git

### Local Setup

1. **Clone the repository**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create .env file**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your local settings

5. **Create PostgreSQL database**
   ```bash
   createdb football_predictor_db
   ```

6. **Run migrations**
   ```bash
   alembic upgrade head
   ```

7. **Seed initial data (optional)**
   ```bash
   python -m app.seed_data
   ```

8. **Start the server**
   ```bash
   uvicorn app.main:app --reload
   ```

   Server will be available at `http://localhost:8000`
   API docs at `http://localhost:8000/docs`

## Using Docker (Optional)

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up -d
   ```

2. **View logs**
   ```bash
   docker-compose logs -f app
   ```

3. **Stop services**
   ```bash
   docker-compose down
   ```

## Development

### Running Tests

```bash
pytest tests/ -v --cov=app
```

### Code Formatting

```bash
black app/
isort app/
flake8 app/
```

### Database Migrations

Create a new migration:
```bash
alembic revision --autogenerate -m "Description of changes"
```

Apply migrations:
```bash
alembic upgrade head
```

## API Documentation

Once the server is running, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Configuration

See `.env.example` for all available configuration options.

Key configurations:
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `SECRET_KEY` - JWT secret key
- `API_FOOTBALL_KEY` - Optional API-Football subscription key

## Troubleshooting

### Database connection fails
```bash
# Check PostgreSQL is running
psql --version

# Verify database exists
psql -l | grep football

# Check connection string in .env
```

### Port 8000 already in use
```bash
# Find process using port 8000
lsof -i :8000

# Or use different port
uvicorn app.main:app --reload --port 8001
```

### Import errors
```bash
# Reinstall requirements
pip install -r requirements.txt --force-reinstall
```

## Contributing

1. Create feature branch: `git checkout -b feature/your-feature`
2. Follow code style with Black and isort
3. Write tests for new features
4. Submit PR with description

## Documentation

- [API Documentation](../API_DOCUMENTATION.md)
- [Database Schema](../DATABASE_SCHEMA.md)
- [Requirements](../REQUIREMENTS.md)

## License

[To be determined]
