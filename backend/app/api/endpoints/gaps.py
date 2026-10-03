"""
gaps.py — Skill gap matrix and trade ranking endpoints.
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.intelligence import SkillGap
from app.models.geography import District, State
from app.models.taxonomy import Sector, Trade
from app.schemas.gap import (
    SkillGapItem, GapMatrixResponse, RankedTradeItem, RankingsResponse
)

router = APIRouter(tags=["Skill Gaps"])


def _gap_to_item(r: SkillGap, db: Session) -> SkillGapItem:
    district = db.query(District).filter(District.id == r.district_id).first()
    sector = db.query(Sector).filter(Sector.id == r.sector_id).first()
    trade = db.query(Trade).filter(Trade.id == r.trade_id).first()
    return SkillGapItem(
        id=r.id,
        district_id=r.district_id,
        sector_id=r.sector_id,
        trade_id=r.trade_id,
        year=r.year,
        demand_value=r.demand_value or 0,
        supply_value=r.supply_value or 0,
        net_gap=r.net_gap or 0,
        gap_ratio_pct=r.gap_ratio_pct or 0.0,
        status=r.status or "BALANCED",
        severity_score=r.severity_score or 0.0,
        urgency_tier=r.urgency_tier or "None",
        diagnostic_explanation=r.diagnostic_explanation or "",
        is_forecast=r.is_forecast or False,
        district_name=district.name if district else "",
        sector_name=sector.name if sector else "",
        trade_name=trade.name if trade else "",
    )


@router.get("/skill-gaps", response_model=GapMatrixResponse)
def get_skill_gaps(
    district_id: Optional[int] = Query(None),
    sector_id: Optional[int] = Query(None),
    trade_id: Optional[int] = Query(None),
    year: Optional[int] = Query(None),
    status: Optional[str] = Query(None, description="SHORTAGE | BALANCED | OVERSUPPLY"),
    is_forecast: Optional[bool] = Query(None),
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db),
):
    """Return filtered skill gap matrix."""
    q = db.query(SkillGap)
    if district_id:
        q = q.filter(SkillGap.district_id == district_id)
    if sector_id:
        q = q.filter(SkillGap.sector_id == sector_id)
    if trade_id:
        q = q.filter(SkillGap.trade_id == trade_id)
    if year:
        q = q.filter(SkillGap.year == year)
    if status:
        q = q.filter(SkillGap.status == status.upper())
    if is_forecast is not None:
        q = q.filter(SkillGap.is_forecast == is_forecast)

    total = q.count()
    records = q.order_by(SkillGap.year, SkillGap.severity_score.desc()).limit(limit).all()

    items = [_gap_to_item(r, db) for r in records]
    shortages = sum(1 for i in items if i.status == "SHORTAGE")
    oversupply = sum(1 for i in items if i.status == "OVERSUPPLY")
    balanced = sum(1 for i in items if i.status == "BALANCED")

    return GapMatrixResponse(
        total_records=total,
        shortages=shortages,
        oversupply=oversupply,
        balanced=balanced,
        items=items,
    )


@router.get("/rankings", response_model=RankingsResponse)
def get_rankings(
    year: Optional[int] = Query(None),
    top_n: int = Query(10, le=50),
    db: Session = Depends(get_db),
):
    """Return top shortage, oversupply, and near-balanced trades."""
    base_q = db.query(SkillGap)
    if year:
        base_q = base_q.filter(SkillGap.year == year)
    else:
        # Default to latest non-forecast year
        latest = db.query(SkillGap.year).filter(SkillGap.is_forecast == False).order_by(SkillGap.year.desc()).first()
        if latest:
            base_q = base_q.filter(SkillGap.year == latest[0])

    shortage_records = (
        base_q.filter(SkillGap.status == "SHORTAGE")
        .order_by(SkillGap.severity_score.desc())
        .limit(top_n)
        .all()
    )

    oversupply_records = (
        base_q.filter(SkillGap.status == "OVERSUPPLY")
        .order_by(SkillGap.severity_score.desc())
        .limit(top_n)
        .all()
    )

    balanced_records = (
        base_q.filter(SkillGap.status == "BALANCED")
        .order_by(SkillGap.severity_score.asc())
        .limit(top_n)
        .all()
    )

    def to_ranked(r: SkillGap, rank: int) -> RankedTradeItem:
        district = db.query(District).filter(District.id == r.district_id).first()
        sector = db.query(Sector).filter(Sector.id == r.sector_id).first()
        trade = db.query(Trade).filter(Trade.id == r.trade_id).first()
        return RankedTradeItem(
            rank=rank,
            district_id=r.district_id,
            sector_id=r.sector_id,
            trade_id=r.trade_id,
            district_name=district.name if district else "",
            sector_name=sector.name if sector else "",
            trade_name=trade.name if trade else "",
            year=r.year,
            status=r.status or "BALANCED",
            severity_score=r.severity_score or 0.0,
            urgency_tier=r.urgency_tier or "None",
            net_gap=r.net_gap or 0,
            gap_ratio_pct=r.gap_ratio_pct or 0.0,
            diagnostic_explanation=r.diagnostic_explanation or "",
        )

    return RankingsResponse(
        year=year,
        top_shortages=[to_ranked(r, i + 1) for i, r in enumerate(shortage_records)],
        top_oversupply=[to_ranked(r, i + 1) for i, r in enumerate(oversupply_records)],
        near_balanced=[to_ranked(r, i + 1) for i, r in enumerate(balanced_records)],
    )
