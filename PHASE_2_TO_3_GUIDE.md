# Phase 2 → Phase 3: Getting Started Guide

## Quick Start (5 minutes)

### Step 1: Start PostgreSQL

**Option A: Docker (Easiest)**
```bash
cd project-root
docker-compose up postgres
# Or in background:
docker-compose up -d postgres
```

**Option B: Local PostgreSQL**
```bash
# Windows: Start PostgreSQL service
net start postgresql-x64-14

# Mac/Linux:
brew services start postgresql
# or
sudo systemctl start postgresql
```

### Step 2: Configure Environment

Create `backend/.env`:
```env
# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/football_predictor_db
SQLALCHEMY_ECHO=false

# API
SECRET_KEY=dev-secret-key-change-in-production
API_TITLE=Football Predictor API
API_VERSION=0.1.0
ENVIRONMENT=development

# Logging
LOG_LEVEL=info

# Redis (optional for caching)
REDIS_URL=redis://localhost:6379

# External APIs (for Phase 2.5)
FOOTBALL_API_KEY=your_key_here
WEATHER_API_KEY=your_key_here
```

### Step 3: Create Database

```bash
# Using psql directly
psql -U postgres -c "CREATE DATABASE football_predictor_db;"

# Or using Docker container
docker-compose exec postgres psql -U postgres -c "CREATE DATABASE football_predictor_db;"
```

### Step 4: Apply Migrations

```bash
cd backend
python -m alembic upgrade head
```

**Expected Output:**
```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> 20260119_001_initial_schema, Initial schema - create all tables
INFO  [alembic.runtime.migration] Running upgrade 20260119_001_initial_schema -> , 
[success] 
```

### Step 5: Verify Tables

```bash
# Check all tables created
psql -d football_predictor_db -c "\dt"

# Should show:
#  public | h2h_statistics
#  public | injuries
#  public | leagues
#  public | matches
#  public | predictions
#  public | team_form
#  public | teams
#  public | user_predictions
#  public | user_profiles
#  public | users
#  public | weather_data
```

### Step 6: Seed Initial Data (Optional)

```bash
# Will create 3 leagues and ~80 teams
python backend/app/seeds/load_initial_data.py
```

---

## Troubleshooting

### PostgreSQL Connection Refused
```
Error: psycopg2.OperationalError: could not connect to server
Solution: 
1. docker-compose ps  # Check if container running
2. docker-compose logs postgres  # Check logs
3. docker-compose restart postgres  # Restart container
```

### Alembic Error: "Can't connect to database"
```
Error: ArgumentError: Could not parse version...
Solution: 
1. Ensure DATABASE_URL in .env is correct
2. Run: python -m alembic upgrade head
3. Check: psql -d football_predictor_db -c "\dt"
```

### Tables Already Exist
```
If migrating to existing database:
python -m alembic stamp head  # Mark as already migrated
python -m alembic upgrade head  # Apply any new migrations
```

---

## File Structure After Setup

```
backend/
├── .env ✅ (you create this)
├── requirements.txt
├── alembic.ini
├── alembic/
│   ├── versions/
│   │   └── 20260119_001_initial_schema.py
│   ├── env.py
│   ├── script.py.mako
│   └── README.md
├── app/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py ✅ (reads .env)
│   │   └── database.py ✅ (creates engine/session)
│   ├── models/
│   │   ├── __init__.py
│   │   ├── league.py
│   │   ├── team.py
│   │   ├── match.py
│   │   ├── user.py
│   │   ├── injury.py
│   │   ├── prediction.py
│   │   ├── team_form.py
│   │   ├── h2h_statistics.py
│   │   ├── weather_data.py
│   │   ├── user_prediction.py
│   │   └── user_profile.py
│   ├── schemas/ ✅ (Phase 3: Create Pydantic models)
│   ├── routes/ ✅ (Phase 3: Create API endpoints)
│   ├── services/ ✅ (Phase 3: Create business logic)
│   └── main.py ✅ (FastAPI app)
├── tests/
│   ├── __init__.py
│   ├── conftest.py ✅ (pytest fixtures)
│   └── test_models.py ✅ (ORM tests)
└── docker-compose.yml
```

---

## Phase 3 Preview: What We'll Build Next

### 1. Pydantic Schemas (Request/Response Models)
```python
# backend/app/schemas/league.py
class LeagueCreate(BaseModel):
    name: str
    country: str
    season: int

class LeagueResponse(BaseModel):
    id: int
    name: str
    country: str
    season: int
    teams_count: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
```

### 2. API Endpoints
```python
# backend/app/routes/leagues.py
@router.get("/leagues", response_model=List[LeagueResponse])
async def list_leagues(session: AsyncSession = Depends(get_db)):
    result = await session.execute(select(League))
    return result.scalars().all()

@router.post("/leagues", response_model=LeagueResponse)
async def create_league(league: LeagueCreate, session: AsyncSession = Depends(get_db)):
    db_league = League(**league.dict())
    session.add(db_league)
    await session.commit()
    return db_league
```

### 3. Service Layer
```python
# backend/app/services/league_service.py
class LeagueService:
    async def create_league(self, db: AsyncSession, name: str, country: str, season: int):
        league = League(name=name, country=country, season=season)
        db.add(league)
        await db.commit()
        return league
    
    async def get_league_with_teams(self, db: AsyncSession, league_id: int):
        # Eager load teams
        result = await db.execute(
            select(League)
            .where(League.id == league_id)
            .options(selectinload(League.teams))
        )
        return result.scalars().first()
```

---

## Testing the Setup

### Quick Python Test
```bash
cd backend
python3 << 'EOF'
import asyncio
from sqlalchemy import select
from app.core.database import async_session
from app.models import League

async def test():
    async with async_session() as session:
        result = await session.execute(select(League))
        leagues = result.scalars().all()
        print(f"✅ Database connected! Found {len(leagues)} leagues")

asyncio.run(test())
EOF
```

### Expected Output
```
✅ Database connected! Found 0 leagues
```

---

## Next: Phase 3 Checklist

- [ ] Database running and accessible
- [ ] Migration applied successfully
- [ ] All 11 tables exist in database
- [ ] Create Pydantic schemas for all models
- [ ] Build CRUD endpoints for League model
- [ ] Build CRUD endpoints for Team model
- [ ] Build CRUD endpoints for Match model
- [ ] Add authentication/user registration
- [ ] Add prediction endpoints
- [ ] Test with Swagger UI at http://localhost:8000/docs

---

## Useful Commands

```bash
# Run backend
cd backend && uvicorn app.main:app --reload

# View API docs
# Open: http://localhost:8000/docs

# Test database connection
psql -d football_predictor_db -c "\dt"

# View migration history
python -m alembic history

# Rollback last migration (if needed)
python -m alembic downgrade -1

# Create new model migration (after modifying models)
python -m alembic revision --autogenerate -m "Add new field to Team"
python -m alembic upgrade head
```

---

## What's Next?

You've completed Phase 2: Database Models! 🎉

**Next Phase (Phase 3):** API Development
- Estimate: 6-8 hours
- Main tasks: Schemas → Endpoints → Authentication
- Outcome: Fully functional REST API with CRUD operations

Ready to start Phase 3? Run this to begin:
```bash
# Start the database first
docker-compose up postgres

# Then let me know and we'll build the API layer!
```
