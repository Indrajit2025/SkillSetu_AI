"""
forecast_router.py — Forecast timeline endpoints.
Returns historical vs forecasted demand/supply for a district/sector/trade.
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.intelligence import Forecast, ModelRun, SkillGap
from app.models.labour_market import LabourDemand, TrainingSupply
from app.models.geography import District
from app.models.taxonomy import Sector, Trade
from app.schemas.forecast import (
    ForecastPoint, ForecastResponse, HistoricalVsForecastPoint, ModelComparisonPoint
)

router = APIRouter(tags=["Forecasts"])


@router.get("/forecast", response_model=ForecastResponse)
def get_forecast(
    district_id: int = Query(...),
    sector_id: int = Query(...),
    trade_id: int = Query(...),
    db: Session = Depends(get_db),
):
    """
    Return full historical + forecasted demand/supply timeline for a
    district × sector × trade combination, with model comparison metrics.
    """
    district = db.query(District).filter(District.id == district_id).first()
    sector = db.query(Sector).filter(Sector.id == sector_id).first()
    trade = db.query(Trade).filter(Trade.id == trade_id).first()

    # Historical records (actual)
    demand_hist = (
        db.query(LabourDemand)
        .filter(
            LabourDemand.district_id == district_id,
            LabourDemand.sector_id == sector_id,
            LabourDemand.trade_id == trade_id,
        )
        .order_by(LabourDemand.year)
        .all()
    )
    supply_hist = (
        db.query(TrainingSupply)
        .filter(
            TrainingSupply.district_id == district_id,
            TrainingSupply.sector_id == sector_id,
            TrainingSupply.trade_id == trade_id,
        )
        .order_by(TrainingSupply.year)
        .all()
    )

    # Forecasted records
    forecasts = (
        db.query(Forecast)
        .filter(
            Forecast.district_id == district_id,
            Forecast.sector_id == sector_id,
            Forecast.trade_id == trade_id,
        )
        .order_by(Forecast.forecast_year)
        .all()
    )

    # Build combined timeline (historical + forecast)
    demand_by_year = {r.year: r.estimated_total_demand or 0 for r in demand_hist}
    supply_by_year = {r.year: r.effective_local_supply or 0 for r in supply_hist}
    forecast_by_year = {f.forecast_year: f for f in forecasts}

    all_years = sorted(
        set(demand_by_year.keys()) | set(supply_by_year.keys()) | set(forecast_by_year.keys())
    )

    timeline: List[HistoricalVsForecastPoint] = []
    for yr in all_years:
        if yr in forecast_by_year:
            fc = forecast_by_year[yr]
            timeline.append(
                HistoricalVsForecastPoint(
                    year=yr,
                    actual_demand=None,
                    actual_supply=None,
                    forecasted_demand=fc.forecasted_demand,
                    forecasted_supply=fc.forecasted_supply,
                    demand_lower_bound=fc.demand_lower_bound,
                    demand_upper_bound=fc.demand_upper_bound,
                    supply_lower_bound=fc.supply_lower_bound,
                    supply_upper_bound=fc.supply_upper_bound,
                    is_forecast=True,
                    confidence_score_pct=fc.confidence_score_pct,
                )
            )
        else:
            timeline.append(
                HistoricalVsForecastPoint(
                    year=yr,
                    actual_demand=demand_by_year.get(yr),
                    actual_supply=supply_by_year.get(yr),
                    forecasted_demand=None,
                    forecasted_supply=None,
                    demand_lower_bound=None,
                    demand_upper_bound=None,
                    supply_lower_bound=None,
                    supply_upper_bound=None,
                    is_forecast=False,
                    confidence_score_pct=None,
                )
            )

    # Model comparisons from ModelRun table
    model_runs = db.query(ModelRun).all()
    model_comparisons = [
        ModelComparisonPoint(
            model_name=mr.model_name,
            mae=mr.mae or 0.0,
            rmse=mr.rmse or 0.0,
            mape=mr.mape,
            r2_score=mr.r2_score or 0.0,
            train_years=mr.train_years or "",
            test_year=mr.test_year or 0,
            is_primary=mr.is_primary or False,
        )
        for mr in model_runs
    ]

    # Summary insight based on last historical vs first forecast year
    last_hist_demand = demand_by_year.get(max(demand_by_year.keys(), default=2024), 0) if demand_by_year else 0
    first_fc = forecasts[0] if forecasts else None
    if first_fc and last_hist_demand:
        pct_change = ((first_fc.forecasted_demand - last_hist_demand) / max(last_hist_demand, 1)) * 100
        direction = "increase" if pct_change >= 0 else "decline"
        summary_insight = (
            f"Demand for {trade.name if trade else 'this trade'} in "
            f"{district.name if district else 'this district'} is forecast to "
            f"{direction} by {abs(pct_change):.1f}% in {first_fc.forecast_year} "
            f"relative to the last observed year, based on GradientBoostingRegressor projections."
        )
    else:
        summary_insight = "Insufficient historical data to generate a detailed forecast insight."

    return ForecastResponse(
        district_name=district.name if district else f"District #{district_id}",
        sector_name=sector.name if sector else f"Sector #{sector_id}",
        trade_name=trade.name if trade else f"Trade #{trade_id}",
        timeline=timeline,
        model_comparisons=model_comparisons,
        primary_model="GradientBoostingRegressor",
        summary_insight=summary_insight,
    )
