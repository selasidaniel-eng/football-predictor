# 🚀 Quick Start Reference Card

## Project Structure
```
football-predictor/
├── backend/          # FastAPI Python backend
├── frontend/         # React TypeScript frontend
└── docs/             # Documentation (from previous phase)
```

## Development Commands

### Backend (Python)
```bash
# Setup
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux
pip install -r requirements.txt

# Run
python -m uvicorn app.main:app --reload

# Test
pytest

# Format
black .
isort .
```

### Frontend (Node.js)
```bash
# Setup
cd frontend
npm install

# Run
npm run dev        # Dev server on :5173
npm run build      # Production build
npm run lint       # Check code quality
npm run format     # Format with Prettier
```

### Database (PostgreSQL)
```bash
# Create database & user
createdb football_predictor_db
createuser football_dev
psql -U football_dev -d football_predictor_db

# Connect
psql -U football_dev -d football_predictor_db
```

### Docker
```bash
# Full stack (PostgreSQL + Redis + Backend + Frontend)
docker-compose up

# Single service
docker-compose up backend
docker-compose up postgres

# Logs
docker-compose logs -f backend
```

## URLs During Development
- **Frontend**: http://localhost:5173
- **Backend**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

## Environment Variables
See `.env.example` - copy to `.env` and customize:
```env
DATABASE_URL=postgresql://football_dev:dev_password@localhost:5432/football_predictor_db
REDIS_URL=redis://localhost:6379/0
JWT_SECRET_KEY=your-secret-key
ENVIRONMENT=development
DEBUG=true
```

## Key Files & Purposes

### Backend
| File | Purpose |
|------|---------|
| `app/main.py` | FastAPI app initialization |
| `app/config.py` | Environment settings (Pydantic) |
| `app/database.py` | SQLAlchemy engine & sessions |
| `app/models/` | Database models (create here) |
| `app/schemas/` | Pydantic validation schemas |
| `app/api/` | Route handlers (endpoints) |
| `app/services/` | Business logic & ML |

### Frontend
| File | Purpose |
|------|---------|
| `src/main.tsx` | React entry point |
| `src/App.tsx` | Main component & routing |
| `src/components/` | Reusable React components |
| `src/pages/` | Page components (create here) |
| `src/services/api.ts` | HTTP client (Axios) |
| `src/hooks/` | Custom React hooks |
| `src/styles/` | CSS & Tailwind styles |

## Testing the Connection

### Test Backend Health
```bash
curl http://localhost:8000/health
```

### Test API Endpoint
```bash
curl http://localhost:8000/api/v1
```

### Test from Browser Console
```javascript
fetch('http://localhost:8000/health')
  .then(r => r.json())
  .then(d => console.log(d))
```

## Workflow

1. **Start Backend** (Terminal 1)
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload
   ```

2. **Start Frontend** (Terminal 2)
   ```bash
   cd frontend
   npm run dev
   ```

3. **Visit App**: http://localhost:5173

4. **Edit Code** → Auto-reload on save (both backend & frontend)

5. **Check Docs**: http://localhost:8000/docs (Swagger UI)

## Next Phase: Database Models

Edit `backend/app/models/` to create SQLAlchemy models for:
- League, Team, Match, Prediction, Injury
- TeamForm, H2HStatistics, WeatherData
- User, UserPrediction, UserProfile

Reference: [DATABASE_SCHEMA.md](docs/DATABASE_SCHEMA.md)

## Documentation
- **Setup**: [SETUP_GUIDE.md](SETUP_GUIDE.md)
- **Phase Status**: [PHASE1_COMPLETE.md](PHASE1_COMPLETE.md)
- **Full Roadmap**: [docs/ROADMAP.md](docs/ROADMAP.md)
- **API Design**: [docs/API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md)
- **Database**: [docs/DATABASE_SCHEMA.md](docs/DATABASE_SCHEMA.md)

## Troubleshooting

**"Module not found" in backend?**
```bash
# Ensure venv is active and requirements installed
pip install -r requirements.txt
```

**Port already in use?**
```bash
# Kill process on port
lsof -ti:8000 | xargs kill -9  # macOS/Linux
netstat -ano | findstr :8000   # Windows
```

**React component not updating?**
- Check for unused imports (eslint warnings)
- Ensure CSS imported in component or globals.css
- Check React dev tools for state issues

## Key Decisions Made

- ✅ FastAPI + SQLAlchemy (async-native)
- ✅ React + TypeScript (type safety)
- ✅ PostgreSQL (relational, ACID)
- ✅ Redis (caching, sessions)
- ✅ Tailwind CSS (utility-first styling)
- ✅ Vite (fast build tool)
- ✅ Docker (consistent environment)

## Timeline
- **Week 1** ✅ (Phase 1: Setup - COMPLETE)
- **Week 2-3**: Data Pipeline (scraper, feature engineering)
- **Week 4-5**: ML Models (training, validation)
- **Week 6-7**: Frontend Pages (match details, dashboard)
- **Week 8-9**: Testing, Polish, Deployment

---

**📖 Start here**: [SETUP_GUIDE.md](SETUP_GUIDE.md)
**🎯 Current status**: [PHASE1_COMPLETE.md](PHASE1_COMPLETE.md)

