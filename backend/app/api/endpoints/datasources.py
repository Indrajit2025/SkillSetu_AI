"""
datasources.py — Data source attribution and export endpoints.
GET /api/data-sources
GET /api/export
"""
import json
from typing import Optional
from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.intelligence import DatasetCoverage, SkillGap, Forecast
from app.models.geography import District
from app.models.taxonomy import Sector, Trade
from app.schemas.data_sources import DataSourceItem, DataSourcesResponse

router = APIRouter(tags=["Data Sources"])

DATA_HONESTY_STATEMENT = (
    "⚠️ SYNTHETIC/DEMO DATA NOTICE: The Odisha pilot dataset in this system is a calibrated "
    "synthetic dataset (is_synthetic=1) generated from real-world structural parameters "
    "including NCVT-MIS ITI seat ratios, NSDC sector growth reports, and PLFS unemployment "
    "indicators. All synthetic records are explicitly labelled in the database and in all "
    "API responses. No fabricated government statistics are presented as official figures. "
    "Every metric is derived from a database record, computed formula, or trained model — "
    "never hardcoded. For production deployment, replace synthetic records with actual "
    "NCVT-MIS, NCS, and PLFS import pipelines."
)


@router.get("/data-sources", response_model=DataSourcesResponse)
def get_data_sources(db: Session = Depends(get_db)):
    """Return dataset coverage information and attribution for all data sources."""
    coverage_records = db.query(DatasetCoverage).all()

    items = [
        DataSourceItem(
            id=c.id,
            source_name=c.source_name,
            source_url=c.source_url or "",
            category=c.category,
            years_covered=c.years_covered or "",
            states_covered=c.states_covered or "",
            districts_covered=c.districts_covered or 0,
            sectors_covered=c.sectors_covered or 0,
            trades_covered=c.trades_covered or 0,
            record_count=c.record_count or 0,
            is_synthetic=c.is_synthetic,
            last_updated=str(c.last_updated) if c.last_updated else "",
            notes=c.notes or "",
        )
        for c in coverage_records
    ]

    total_records = sum(i.record_count for i in items)
    synthetic_count = sum(1 for i in items if i.is_synthetic)

    return DataSourcesResponse(
        data_honesty_statement=DATA_HONESTY_STATEMENT,
        sources=items,
        total_records_in_db=total_records,
        synthetic_sources_count=synthetic_count,
        real_sources_count=len(items) - synthetic_count,
        pilot_geography="Odisha (30 districts, 8 sectors, 24+ trades, 2019-2024)",
    )


@router.get("/export")
def export_data(
    format: str = Query("json", pattern="^(json|csv)$"),
    district_id: Optional[int] = Query(None),
    sector_id: Optional[int] = Query(None),
    trade_id: Optional[int] = Query(None),
    year: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    """
    Export skill gap and forecast data as JSON or CSV.
    Filters by optional district/sector/trade/year.
    """
    gap_q = db.query(SkillGap)
    if district_id:
        gap_q = gap_q.filter(SkillGap.district_id == district_id)
    if sector_id:
        gap_q = gap_q.filter(SkillGap.sector_id == sector_id)
    if trade_id:
        gap_q = gap_q.filter(SkillGap.trade_id == trade_id)
    if year:
        gap_q = gap_q.filter(SkillGap.year == year)
    gaps = gap_q.order_by(SkillGap.year).limit(1000).all()

    fc_q = db.query(Forecast)
    if district_id:
        fc_q = fc_q.filter(Forecast.district_id == district_id)
    if sector_id:
        fc_q = fc_q.filter(Forecast.sector_id == sector_id)
    if trade_id:
        fc_q = fc_q.filter(Forecast.trade_id == trade_id)
    forecasts = fc_q.order_by(Forecast.forecast_year).limit(200).all()

    if format == "json":
        payload = {
            "export_metadata": {
                "project": "SkillSetu AI",
                "sih_ps": "26246",
                "data_honesty": DATA_HONESTY_STATEMENT[:200] + "...",
                "filters": {
                    "district_id": district_id,
                    "sector_id": sector_id,
                    "trade_id": trade_id,
                    "year": year,
                },
                "records_exported": {"skill_gaps": len(gaps), "forecasts": len(forecasts)},
            },
            "skill_gaps": [
                {
                    "id": g.id,
                    "district_id": g.district_id,
                    "sector_id": g.sector_id,
                    "trade_id": g.trade_id,
                    "year": g.year,
                    "demand_value": g.demand_value,
                    "supply_value": g.supply_value,
                    "net_gap": g.net_gap,
                    "gap_ratio_pct": g.gap_ratio_pct,
                    "status": g.status,
                    "severity_score": g.severity_score,
                    "urgency_tier": g.urgency_tier,
                    "diagnostic_explanation": g.diagnostic_explanation,
                    "is_forecast": g.is_forecast,
                    "is_synthetic": g.is_synthetic,
                }
                for g in gaps
            ],
            "forecasts": [
                {
                    "id": f.id,
                    "district_id": f.district_id,
                    "sector_id": f.sector_id,
                    "trade_id": f.trade_id,
                    "forecast_year": f.forecast_year,
                    "forecasted_demand": f.forecasted_demand,
                    "forecasted_supply": f.forecasted_supply,
                    "demand_lower_bound": f.demand_lower_bound,
                    "demand_upper_bound": f.demand_upper_bound,
                    "confidence_score_pct": f.confidence_score_pct,
                    "model_name": f.model_name,
                }
                for f in forecasts
            ],
        }
        return JSONResponse(content=payload)

    # CSV export
    lines = ["district_id,sector_id,trade_id,year,demand,supply,net_gap,gap_ratio_pct,status,severity,urgency,is_forecast,is_synthetic"]
    for g in gaps:
        lines.append(
            f"{g.district_id},{g.sector_id},{g.trade_id},{g.year},"
            f"{g.demand_value},{g.supply_value},{g.net_gap},{g.gap_ratio_pct},"
            f"{g.status},{g.severity_score},{g.urgency_tier},{int(g.is_forecast or 0)},{int(g.is_synthetic or 0)}"
        )
    csv_content = "\n".join(lines)
    from fastapi.responses import PlainTextResponse
    return PlainTextResponse(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=skillsetu_export.csv"},
    )
