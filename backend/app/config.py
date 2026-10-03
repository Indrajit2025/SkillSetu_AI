import os
from pydantic_settings import BaseSettings
from typing import List, Dict

class Settings(BaseSettings):
    PROJECT_NAME: str = "SkillSetu AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    DESCRIPTION: str = "AI-Enabled Labour Market Intelligence and Skill Demand-Supply Forecasting Engine (SIH Problem Statement 26246)"
    
    # Environment & Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "skillsetu_sih_super_secure_jwt_secret_key_2026_production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Database
    # Defaults to SQLite local file for zero-config out-of-the-box run, easily overriden to PostgreSQL via .env
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./skillsetu.db")
    
    # CORS Origins: reads from env var CORS_ORIGINS or allows all origins for deployment flexibility
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "*"
    ]
    
    # Configurable Demand Index Weights (Must sum to 1.0)
    DEMAND_WEIGHT_JOB_POSTINGS: float = 0.35
    DEMAND_WEIGHT_HIRING_GROWTH: float = 0.25
    DEMAND_WEIGHT_SECTOR_GVA_GROWTH: float = 0.20
    DEMAND_WEIGHT_INVESTMENT_INFLOWS: float = 0.20
    
    # Configurable Supply Index Weights (Must sum to 1.0)
    SUPPLY_WEIGHT_SANCTIONED_SEATS: float = 0.30
    SUPPLY_WEIGHT_ENROLMENTS: float = 0.35
    SUPPLY_WEIGHT_COMPLETIONS_PASSOUTS: float = 0.35
    
    # Skill Gap Classification Thresholds (Normalized Gap Ratio: (Demand - Supply) / (Demand + Supply + epsilon))
    SHORTAGE_THRESHOLD: float = 0.15      # > +15% net difference is Shortage
    OVERSUPPLY_THRESHOLD: float = -0.15   # < -15% net difference is Oversupply
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
