# Football Bet Predictor Website

A machine learning-powered football prediction system built with FastAPI, React, and PostgreSQL.

**Status:** Week 1 Phase 1 - Project Initialization Started ✅  
**Created:** January 19, 2026  
**Target Launch:** March 20, 2026  

---

## 📖 DOCUMENTATION

All project documentation is in the `docs/` folder. Start with these in order:

1. **00_READ_ME_FIRST.md** - Quick overview and dashboard
2. **README.md** - Complete project overview  
3. **REQUIREMENTS.md** - Detailed specifications (41 FR, 27 NFR)
4. **ROADMAP.md** - Implementation timeline (9 weeks)
5. **DATABASE_SCHEMA.md** - PostgreSQL design (11 tables)
6. **API_DOCUMENTATION.md** - REST API specification (24+ endpoints)

**Location:** `c:\Users\deyou\Saved Games\c\` (original documentation)

---

## 🏗️ PROJECT STRUCTURE

```
football-predictor/
├── backend/                  # FastAPI backend
│   ├── app/                  # Main application code
│   │   ├── models/          # Database ORM models
│   │   ├── schemas/         # Pydantic request/response
│   │   ├── api/             # API route handlers
│   │   ├── services/        # Business logic
│   │   └── utils/           # Helper functions
│   ├── tests/               # Unit & integration tests
│   ├── migrations/          # Alembic database migrations
│   ├── requirements.txt    # Python dependencies
│   ├── Dockerfile
│   └── README.md
├── frontend/                 # React + TypeScript frontend
│   ├── src/
│   │   ├── components/      # Reusable React components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API client
│   │   ├── hooks/          # Custom React hooks
│   │   └── styles/         # Tailwind CSS
│   ├── public/             # Static assets
│   ├── package.json        # Node dependencies
│   ├── vite.config.ts
│   ├── Dockerfile
│   └── README.md
├── docs/                    # Original documentation
├── .env.example             # Environment template
├── .gitignore              # Git ignore file
└── README.md               # This file
```

---

## 🚀 QUICK START

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
copy ..\env.example .env
# Edit .env with your settings

# Create PostgreSQL database
createdb football_predictor_db

# Start development server
uvicorn app.main:app --reload
```

**Backend:** http://localhost:8000  
**API Docs:** http://localhost:8000/docs

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env file (from root)
copy ..\.env.example .env.local
# Edit .env.local with your settings

# Start development server
npm run dev
```

**Frontend:** http://localhost:5173

---

## 📅 CURRENT PHASE

### Week 1 Phase 1: Project Initialization ✅

**Completed:**
- [x] Project folder structure created
- [x] Git repository initialized
- [x] Python requirements.txt created
- [x] Node package.json created
- [x] .env.example template created
- [x] Backend README created
- [x] Frontend README created
- [x] .gitignore created

**Next Steps (This Week):**
- [ ] Set up PostgreSQL database locally
- [ ] Create FastAPI skeleton (main.py, config, logging)
- [ ] Create React skeleton (Vite, Tailwind, routing)
- [ ] Test local connections
- [ ] Commit to Git

**Estimated Time:** 3-4 hours (Monday-Tuesday)

---

## 🛠️ TECH STACK

| Component | Technology | Version |
|-----------|-----------|---------|
| **Backend** | FastAPI | 0.104+ |
| **Frontend** | React + TypeScript | 18.2+ |
| **Database** | PostgreSQL | 14+ |
| **Cache** | Redis | 7+ |
| **ML** | scikit-learn + XGBoost | Latest |
| **Scraping** | Playwright | 1.40+ |
| **Deployment** | Railway | - |

---

## 📋 REQUIREMENTS

See [REQUIREMENTS.md](../docs/REQUIREMENTS.md) for complete specifications:

- **41 Functional Requirements** (FR-1 to FR-41)
- **27 Non-Functional Requirements** (NFR-1 to NFR-27)
- **Acceptance Criteria** for MVP launch

---

## 📅 TIMELINE

**6 Phases, 9 Weeks, 154 Hours**

| Phase | Weeks | Duration | Status |
|-------|-------|----------|--------|
| Phase 1: Foundation | 1-2 | 28 hrs | ✅ Starting |
| Phase 2: Data Pipeline | 3-4 | 33 hrs | ⏳ Next |
| Phase 3: ML Models | 5-6 | 26 hrs | ⏳ Next |
| Phase 4: Frontend | 7 | 29 hrs | ⏳ Next |
| Phase 5: Integration | 8 | 29 hrs | ⏳ Next |
| Phase 6: Deployment | 9 | 9 hrs | ⏳ Next |

**Target Launch:** March 20, 2026

See [ROADMAP.md](../docs/ROADMAP.md) for detailed week-by-week breakdown.

---

## 🎯 MVP SCOPE

**Included:**
- 3 football leagues (Premier League, La Liga, Bundesliga)
- Match outcome predictions (1/X/2 with confidence)
- Goal predictions (Over/Under 2.5)
- User authentication (email/password)
- User dashboard (saved predictions, bet tracking)
- Real-time match score updates
- Team statistics and analysis
- Injury tracking
- Odds comparison

**Not Included (Phase 2+):**
- Mobile native app
- WebSocket real-time
- Multi-language support
- Advanced xG analytics
- Betting execution
- Email notifications

---

## 📖 FEATURE BREAKDOWN

### Prediction Engine (Phase 3)
- ML model predictions with confidence scores
- Key factors explanation
- Prediction history tracking
- Weekly model retraining

### Data Collection (Phase 2)
- Web scraping (sofascore.com, livescore.com)
- Injury data tracking
- Team form metrics
- H2H statistics
- Weather integration
- Real-time score updates

### Frontend (Phase 4)
- Homepage with upcoming matches
- Match detail page with statistics
- User dashboard
- Login/registration pages
- Prediction saving & tracking

### User Features
- Email/password authentication
- Save predictions
- Track betting accuracy
- View personal statistics
- Manage profile settings

---

## 🧪 TESTING

```bash
# Backend tests
cd backend
pytest tests/ -v --cov=app

# Frontend tests (when implemented)
cd frontend
npm test
```

---

## 📊 DATABASE

PostgreSQL with 11 tables:

1. `leagues` - Football league info
2. `teams` - Team data
3. `matches` - Match records
4. `predictions` - ML predictions
5. `injuries` - Player injuries
6. `team_form` - Team performance
7. `h2h_statistics` - Head-to-head records
8. `weather_data` - Weather conditions
9. `users` - User accounts
10. `user_predictions` - Saved bets
11. `user_profile` - User statistics

See [DATABASE_SCHEMA.md](../docs/DATABASE_SCHEMA.md) for complete schema.

---

## 🔗 API

24+ REST endpoints documented in [API_DOCUMENTATION.md](../docs/API_DOCUMENTATION.md):

- Authentication (4 endpoints)
- Matches (3 endpoints)
- Predictions (2 endpoints)
- User predictions (4 endpoints)
- User dashboard (2 endpoints)
- Teams & leagues (3 endpoints)
- Injuries (1 endpoint)

---

## 🚀 DEPLOYMENT

**Target:** Railway.app

- Automatic PostgreSQL setup
- Managed Redis
- Auto-scaling
- ~$20-50/month for MVP tier

See deployment guide in documentation.

---

## 📞 SUPPORT

**All questions answered in documentation:**

- What should this do? → REQUIREMENTS.md
- How do I store data? → DATABASE_SCHEMA.md
- What should API return? → API_DOCUMENTATION.md
- When is it due? → ROADMAP.md
- What's the overview? → 00_READ_ME_FIRST.md

---

## ✅ CHECKLIST - WEEK 1

- [x] Create project structure
- [x] Initialize Git
- [x] Create requirements.txt (Python)
- [x] Create package.json (Node)
- [ ] Install Python 3.11+
- [ ] Install Node 18+
- [ ] Install PostgreSQL 14+
- [ ] Install Redis (optional for local dev)
- [ ] Install Playwright browsers
- [ ] Set up local PostgreSQL database
- [ ] Test backend connections
- [ ] Test frontend connections
- [ ] Make initial Git commit

---

## 🤝 CONTRIBUTING

1. Create feature branch: `git checkout -b feature/your-feature`
2. Follow code standards (Black, flake8, ESLint)
3. Write tests for new features
4. Commit with clear message: `git commit -m "Add feature X"`
5. Push and create PR

---

## 📄 LICENSE

[To be determined]

---

## 📞 QUESTIONS?

All answers are in the [documentation folder](../docs/).

- Stuck? → Search the docs
- Wrong? → Check REQUIREMENTS.md
- Timeline? → Check ROADMAP.md
- Database? → Check DATABASE_SCHEMA.md
- API? → Check API_DOCUMENTATION.md

---

**Status:** Week 1 Phase 1 - Foundation Setup  
**Created:** January 19, 2026  
**Ready to build!** 🚀
