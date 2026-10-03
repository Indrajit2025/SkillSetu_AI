"""
scenarios.py — What-If scenario simulation endpoint.
POST /api/scenarios  ->  ScenarioSimulationResult
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.intelligence import SkillGap, ScenarioRun
from app.models.geography import District
from app.models.taxonomy import Sector, Trade
from app.schemas.scenario import ScenarioSimulationRequest, ScenarioSimulationResult
from app.services.scenario_service import scenario_service

router = APIRouter(tags=["Scenarios"])


@router.post("/scenarios", response_model=ScenarioSimulationResult)
def run_scenario(
    request: ScenarioSimulationRequest,
    db: Session = Depends(get_db),
):
    """
    What-If Simulator.

    Given a district/sector/trade/year and intervention parameters, 
    recalculates supply, demand, gap, classification, and severity.
    Returns baseline vs scenario comparison with a multi-year timeline.
    """
    # Validate geography/taxonomy
    district = db.query(District).filter(District.id == request.district_id).first()
    if not district:
        raise HTTPException(status_code=404, detail=f"District {request.district_id} not found")

    sector = db.query(Sector).filter(Sector.id == request.sector_id).first()
    if not sector:
        raise HTTPException(status_code=404, detail=f"Sector {request.sector_id} not found")

    trade = db.query(Trade).filter(Trade.id == request.trade_id).first()
    if not trade:
        raise HTTPException(status_code=404, detail=f"Trade {request.trade_id} not found")

    # Fetch baseline gap record for target year (or closest available)
    gap_record = (
        db.query(SkillGap)
        .filter(
            SkillGap.district_id == request.district_id,
            SkillGap.sector_id == request.sector_id,
            SkillGap.trade_id == request.trade_id,
            SkillGap.year == request.target_year,
        )
        .first()
    )

    if not gap_record:
        # Fall back to latest available year
        gap_record = (
            db.query(SkillGap)
            .filter(
                SkillGap.district_id == request.district_id,
                SkillGap.sector_id == request.sector_id,
                SkillGap.trade_id == request.trade_id,
            )
            .order_by(SkillGap.year.desc())
            .first()
        )

    if not gap_record:
        raise HTTPException(
            status_code=404,
            detail=(
                f"No baseline data found for District={request.district_id}, "
                f"Sector={request.sector_id}, Trade={request.trade_id}. "
                "Please seed the database first."
            ),
        )

    baseline_demand = gap_record.demand_value or 1000
    baseline_supply = gap_record.supply_value or 500

    # Fetch multi-year forecast timeline from SkillGap (is_forecast=True)
    forecast_gaps = (
        db.query(SkillGap)
        .filter(
            SkillGap.district_id == request.district_id,
            SkillGap.sector_id == request.sector_id,
            SkillGap.trade_id == request.trade_id,
            SkillGap.is_forecast == True,
        )
        .order_by(SkillGap.year)
        .all()
    )
    year_forecasts = [
        {"year": g.year, "demand": g.demand_value or baseline_demand, "supply": g.supply_value or baseline_supply}
        for g in forecast_gaps
    ]

    result = scenario_service.run_simulation(
        baseline_demand=baseline_demand,
        baseline_supply=baseline_supply,
        request=request,
        district_name=district.name,
        sector_name=sector.name,
        trade_name=trade.name,
        year_forecasts=year_forecasts,
    )

    # Persist scenario run to database
    try:
        run = ScenarioRun(
            district_id=request.district_id,
            sector_id=request.sector_id,
            trade_id=request.trade_id,
            target_year=request.target_year,
            additional_seats=request.additional_seats,
            intake_expansion_pct=request.intake_expansion_pct,
            demand_surge_pct=request.demand_surge_pct,
            placement_boost_pct=request.placement_boost_pct,
            scenario_name=request.scenario_name or "Custom Scenario",
            baseline_gap=result.baseline_net_gap,
            scenario_gap=result.scenario_net_gap,
            baseline_status=result.baseline_status,
            scenario_status=result.scenario_status,
            baseline_severity=result.baseline_severity_score,
            scenario_severity=result.scenario_severity_score,
            policy_impact_summary=result.policy_impact_summary,
        )
        db.add(run)
        db.commit()
    except Exception:
        db.rollback()  # Don't fail the response if persistence fails

    return result
