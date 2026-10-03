"""
market.py — Demand / Supply market data endpoints.
Provides time-series demand and supply records for a given district/sector/trade combination.
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.labour_market import LabourDemand, TrainingSupply
from app.models.taxonomy import Sector, Trade
from app.models.geography import District
from app.schemas.market import (
    DemandSeriesPoint, SupplySeriesPoint, MarketDetailsResponse,
    DistrictItem, SectorItem, TradeItem
)
from app.config import settings

router = APIRouter(tags=["Market Data"])


@router.get("/demand", response_model=List[DemandSeriesPoint])
def get_demand(
    district_id: Optional[int] = Query(None),
    sector_id: Optional[int] = Query(None),
    trade_id: Optional[int] = Query(None),
    year: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    """Return LabourDemand records filtered by optional district/sector/trade/year."""
    q = db.query(LabourDemand)
    if district_id:
        q = q.filter(LabourDemand.district_id == district_id)
    if sector_id:
        q = q.filter(LabourDemand.sector_id == sector_id)
    if trade_id:
        q = q.filter(LabourDemand.trade_id == trade_id)
    if year:
        q = q.filter(LabourDemand.year == year)
    records = q.order_by(LabourDemand.year).all()

    return [
        DemandSeriesPoint(
            id=r.id,
            district_id=r.district_id,
            sector_id=r.sector_id,
            trade_id=r.trade_id,
            year=r.year,
            job_postings_count=r.job_postings_count or 0,
            hiring_growth_rate_pct=r.hiring_growth_rate_pct or 0.0,
            gva_growth_pct=r.gva_growth_pct or 0.0,
            investment_inflow_crores=r.investment_inflow_crores or 0.0,
            normalized_demand_index=r.normalized_demand_index or 0.0,
            estimated_total_demand=r.estimated_total_demand or 0,
            is_synthetic=r.is_synthetic,
        )
        for r in records
    ]


@router.get("/supply", response_model=List[SupplySeriesPoint])
def get_supply(
    district_id: Optional[int] = Query(None),
    sector_id: Optional[int] = Query(None),
    trade_id: Optional[int] = Query(None),
    year: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    """Return TrainingSupply records filtered by optional district/sector/trade/year."""
    q = db.query(TrainingSupply)
    if district_id:
        q = q.filter(TrainingSupply.district_id == district_id)
    if sector_id:
        q = q.filter(TrainingSupply.sector_id == sector_id)
    if trade_id:
        q = q.filter(TrainingSupply.trade_id == trade_id)
    if year:
        q = q.filter(TrainingSupply.year == year)
    records = q.order_by(TrainingSupply.year).all()

    return [
        SupplySeriesPoint(
            id=r.id,
            district_id=r.district_id,
            sector_id=r.sector_id,
            trade_id=r.trade_id,
            year=r.year,
            sanctioned_seats=r.sanctioned_seats or 0,
            actual_enrolments=r.actual_enrolments or 0,
            passouts=r.passouts or 0,
            local_absorption_rate_pct=r.local_absorption_rate_pct or 0.0,
            effective_local_supply=r.effective_local_supply or 0,
            normalized_supply_index=r.normalized_supply_index or 0.0,
            is_synthetic=r.is_synthetic,
        )
        for r in records
    ]


@router.get("/market-details", response_model=MarketDetailsResponse)
def get_market_details(
    district_id: int = Query(...),
    sector_id: int = Query(...),
    trade_id: int = Query(...),
    db: Session = Depends(get_db),
):
    """Full demand + supply time-series for a specific district/sector/trade combination."""
    district = db.query(District).filter(District.id == district_id).first()
    sector = db.query(Sector).filter(Sector.id == sector_id).first()
    trade = db.query(Trade).filter(Trade.id == trade_id).first()

    demand_records = (
        db.query(LabourDemand)
        .filter(
            LabourDemand.district_id == district_id,
            LabourDemand.sector_id == sector_id,
            LabourDemand.trade_id == trade_id,
        )
        .order_by(LabourDemand.year)
        .all()
    )

    supply_records = (
        db.query(TrainingSupply)
        .filter(
            TrainingSupply.district_id == district_id,
            TrainingSupply.sector_id == sector_id,
            TrainingSupply.trade_id == trade_id,
        )
        .order_by(TrainingSupply.year)
        .all()
    )

    demand_series = [
        DemandSeriesPoint(
            id=r.id,
            district_id=r.district_id,
            sector_id=r.sector_id,
            trade_id=r.trade_id,
            year=r.year,
            job_postings_count=r.job_postings_count or 0,
            hiring_growth_rate_pct=r.hiring_growth_rate_pct or 0.0,
            gva_growth_pct=r.gva_growth_pct or 0.0,
            investment_inflow_crores=r.investment_inflow_crores or 0.0,
            normalized_demand_index=r.normalized_demand_index or 0.0,
            estimated_total_demand=r.estimated_total_demand or 0,
            is_synthetic=r.is_synthetic,
        )
        for r in demand_records
    ]

    supply_series = [
        SupplySeriesPoint(
            id=r.id,
            district_id=r.district_id,
            sector_id=r.sector_id,
            trade_id=r.trade_id,
            year=r.year,
            sanctioned_seats=r.sanctioned_seats or 0,
            actual_enrolments=r.actual_enrolments or 0,
            passouts=r.passouts or 0,
            local_absorption_rate_pct=r.local_absorption_rate_pct or 0.0,
            effective_local_supply=r.effective_local_supply or 0,
            normalized_supply_index=r.normalized_supply_index or 0.0,
            is_synthetic=r.is_synthetic,
        )
        for r in supply_records
    ]

    return MarketDetailsResponse(
        district_name=district.name if district else f"District #{district_id}",
        sector_name=sector.name if sector else f"Sector #{sector_id}",
        trade_name=trade.name if trade else f"Trade #{trade_id}",
        demand_series=demand_series,
        supply_series=supply_series,
        demand_weight_config={
            "job_postings": settings.DEMAND_WEIGHT_JOB_POSTINGS,
            "hiring_growth": settings.DEMAND_WEIGHT_HIRING_GROWTH,
            "gva_growth": settings.DEMAND_WEIGHT_SECTOR_GVA_GROWTH,
            "investment": settings.DEMAND_WEIGHT_INVESTMENT_INFLOWS,
        },
        supply_weight_config={
            "sanctioned_seats": settings.SUPPLY_WEIGHT_SANCTIONED_SEATS,
            "enrolments": settings.SUPPLY_WEIGHT_ENROLMENTS,
            "passouts": settings.SUPPLY_WEIGHT_COMPLETIONS_PASSOUTS,
        },
    )
