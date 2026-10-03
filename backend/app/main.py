import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import engine, Base

# Auto-create tables on startup (for dev/sqlite; in production use Alembic migrations)
Base.metadata.create_all(bind=engine)

# Import all models so SQLAlchemy registers them before create_all
from app.models import (  # noqa: F401
    User, State, District, Sector, Trade, Occupation, OccupationMapping,
    LabourDemand, TrainingSupply, LabourIndicator,
    Forecast, SkillGap, ModelRun, ScenarioRun, DatasetCoverage
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s"
)
logger = logging.getLogger("skillsetu")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 SkillSetu AI Backend starting up...")
    logger.info(f"   Database: {settings.DATABASE_URL.split('://')[0]}")
    logger.info(f"   Version : {settings.VERSION}")
    yield
    logger.info("🛑 SkillSetu AI Backend shutting down.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Global exception handler ──────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error on {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Please try again or contact support."}
    )


# ── Routers ───────────────────────────────────────────────────────────────────
from app.api.endpoints import auth, overview, market, gaps, forecast_router, scenarios, evaluation, datasources  # noqa: E402

app.include_router(auth.router,            prefix=settings.API_V1_STR)
app.include_router(overview.router,        prefix=settings.API_V1_STR)
app.include_router(market.router,          prefix=settings.API_V1_STR)
app.include_router(gaps.router,            prefix=settings.API_V1_STR)
app.include_router(forecast_router.router, prefix=settings.API_V1_STR)
app.include_router(scenarios.router,       prefix=settings.API_V1_STR)
app.include_router(evaluation.router,      prefix=settings.API_V1_STR)
app.include_router(datasources.router,     prefix=settings.API_V1_STR)


# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "api_docs": f"{settings.API_V1_STR}/docs"
    }


@app.get("/", tags=["Root"])
def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} API",
        "description": settings.DESCRIPTION,
        "sih_ps": "26246",
        "docs": f"{settings.API_V1_STR}/docs"
    }
