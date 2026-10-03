from pydantic import BaseModel
from typing import List, Optional


class ForecastPoint(BaseModel):
    """A single forecast point for a future year."""
    year: int
    forecasted_demand: int
    forecasted_supply: int
    demand_lower_bound: Optional[int] = None
    demand_upper_bound: Optional[int] = None
    supply_lower_bound: Optional[int] = None
    supply_upper_bound: Optional[int] = None
    confidence_score_pct: Optional[float] = None
    model_name: str = "GradientBoostingRegressor"


class HistoricalVsForecastPoint(BaseModel):
    """One year in the unified historical + forecasted timeline."""
    year: int
    # Historical (actual) fields — None for forecast years
    actual_demand: Optional[int] = None
    actual_supply: Optional[int] = None
    # Forecast fields — None for historical years
    forecasted_demand: Optional[int] = None
    forecasted_supply: Optional[int] = None
    demand_lower_bound: Optional[int] = None
    demand_upper_bound: Optional[int] = None
    supply_lower_bound: Optional[int] = None
    supply_upper_bound: Optional[int] = None
    is_forecast: bool = False
    confidence_score_pct: Optional[float] = None


class ModelComparisonPoint(BaseModel):
    """Evaluation metrics for one model."""
    model_name: str
    mae: float
    rmse: float
    mape: Optional[float] = None
    r2_score: float
    train_years: str = "2019-2023"
    test_year: int = 2024
    is_primary: bool = False


class ForecastResponse(BaseModel):
    """Full forecast response including historical timeline and model comparisons."""
    district_name: str
    sector_name: str
    trade_name: str
    primary_model: str = "GradientBoostingRegressor"
    timeline: List[HistoricalVsForecastPoint]
    model_comparisons: List[ModelComparisonPoint]
    summary_insight: str
