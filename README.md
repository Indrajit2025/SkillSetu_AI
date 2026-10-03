# SkillSetu AI

**AI-Enabled Labour Market Intelligence and Skill Demand-Supply Forecasting Engine**  
SIH Problem Statement: **26246**

---

## Quick Start (Local Dev — One Command)

```bash
# Clone / navigate to backend
cd SkillSetu_AI/backend

# 1. Create virtual environment
python -m venv venv
.\venv\Scripts\activate       # Windows
# source venv/bin/activate    # Mac/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Copy environment file
copy .env.example .env        # Windows
# cp .env.example .env        # Mac/Linux

# 4. Seed database with Odisha pilot data
python seed_data.py

# 5. Start API server
uvicorn app.main:app --reload --port 8000
```

API Docs: http://localhost:8000/api/docs  
Health:   http://localhost:8000/health

---

## Architecture

```
SkillSetu_AI/
├── backend/
│   ├── app/
│   │   ├── config.py            # Settings & configurable weights
│   │   ├── database.py          # SQLAlchemy engine / session
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── models/              # SQLAlchemy ORM models
│   │   │   ├── user.py          # User + RBAC
│   │   │   ├── geography.py     # State + District
│   │   │   ├── taxonomy.py      # Sector, Trade, Occupation, OccupationMapping
│   │   │   ├── labour_market.py # LabourDemand, TrainingSupply, LabourIndicator
│   │   │   └── intelligence.py  # Forecast, SkillGap, ModelRun, ScenarioRun, DatasetCoverage
│   │   ├── schemas/             # Pydantic request/response schemas
│   │   ├── services/            # Business logic engines
│   │   │   ├── auth_service.py          # JWT + password hashing
│   │   │   ├── demand_engine.py         # Demand Index computation
│   │   │   ├── supply_engine.py         # Supply Index computation
│   │   │   ├── diagnostic_explainer.py  # Feature-based gap explanations
│   │   │   ├── forecasting_engine.py    # ML forecasting (GBR, Ridge, Baseline)
│   │   │   ├── skill_gap_service.py     # Gap classification & severity
│   │   │   └── scenario_service.py      # What-If simulation
│   │   └── api/endpoints/       # FastAPI routers
│   │       ├── auth.py          # POST /auth/register, /auth/login, GET /auth/me
│   │       ├── overview.py      # GET /api/overview, /api/states, /api/sectors, /api/trades
│   │       ├── market.py        # GET /api/demand, /api/supply, /api/market-details
│   │       ├── gaps.py          # GET /api/skill-gaps, /api/rankings
│   │       ├── forecast_router.py  # GET /api/forecast
│   │       ├── scenarios.py     # POST /api/scenarios
│   │       ├── evaluation.py    # GET /api/model-evaluation
│   │       └── datasources.py   # GET /api/data-sources, /api/export
│   ├── seed_data.py             # Full Odisha pilot dataset seeder
│   ├── requirements.txt
│   └── .env
└── docs/
    ├── SIH_26246_REQUIREMENTS.md
    ├── DEMO_SCRIPT.md
    ├── PPT_EVIDENCE.md
    └── DATA_SOURCES.md
```

---

## Database

**Default**: SQLite (`skillsetu.db`) — zero configuration, runs immediately.  
**Production**: PostgreSQL — update `DATABASE_URL` in `.env`.

---

## Demo Login Credentials

| Email | Password | Role |
|---|---|---|
| admin@skillsetu.gov.in | Admin@123 | Admin |
| analyst@odisha.gov.in | Analyst@123 | Analyst |
| policy@sdteodiasha.gov.in | Policy@123 | Policy Maker |

---

## Data Honesty Statement

> **⚠️ SYNTHETIC/DEMO DATA NOTICE**: The Odisha pilot dataset used in this application is a calibrated synthetic dataset generated from real-world structural parameters including NCVT-MIS ITI seat ratios, NSDC sector growth reports, and PLFS unemployment indicators. It is explicitly labelled `is_synthetic=1` in the database and displayed with a SYNTHETIC DATA badge in all dashboards. No fabricated government statistics are presented as official figures.

---

## API Reference Summary

| Method | Endpoint | Description |
|---|---|---|
| POST | /api/auth/register | Register new user |
| POST | /api/auth/login | Login, get JWT token |
| GET | /api/auth/me | Get current user profile |
| GET | /api/overview | National dashboard metrics |
| GET | /api/states | All states |
| GET | /api/states/{id}/districts | Districts for a state |
| GET | /api/sectors | All sectors |
| GET | /api/trades | All trades (filter by sector_id) |
| GET | /api/demand | Labour demand records |
| GET | /api/supply | Training supply records |
| GET | /api/market-details | Combined demand+supply for drilldown |
| GET | /api/skill-gaps | Skill gap matrix |
| GET | /api/rankings | Top shortages and oversupply ranking |
| GET | /api/forecast | Forecast timeline for a trade/district |
| POST | /api/scenarios | Run What-If simulation |
| GET | /api/model-evaluation | ML model metrics and comparisons |
| GET | /api/data-sources | Dataset coverage and attribution |
| GET | /api/export | Export data as JSON/CSV |
| GET | /health | Health check |

Full interactive docs at: http://localhost:8000/api/docs
