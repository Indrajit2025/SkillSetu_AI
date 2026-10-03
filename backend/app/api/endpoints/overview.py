"""
overview.py — National / state-level overview dashboard endpoints.

Provides:
  GET /api/overview                       — Aggregated NationalOverview payload.
  GET /api/states                         — All states with district counts.
  GET /api/states/{state_id}/districts    — Districts belonging to a state.
  GET /api/sectors                        — All industry sectors.
  GET /api/trades                         — All trades (optional ?sector_id filter).
  GET /api/districts/{district_id}/trades — Trades with activity in a district.
"""

from collections import defaultdict
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import (
    District,
    LabourDemand,
    Sector,
    SkillGap,
    State,
    Trade,
    TrainingSupply,
)
from app.schemas.market import DistrictItem, SectorItem, StateItem, TradeItem
from app.schemas.overview import (
    DistrictSummaryItem,
    MetricCard,
    NationalOverview,
    SectorDistribution,
)

router = APIRouter(prefix="", tags=["Overview"])

# ── Constants ──────────────────────────────────────────────────────────────────
_OVERVIEW_YEAR = 2024
_TIME_SERIES_YEARS = list(range(2019, 2025))


# ── /api/overview ──────────────────────────────────────────────────────────────
@router.get(
    "/overview",
    response_model=NationalOverview,
    summary="National labour market overview",
    description=(
        "Returns a comprehensive aggregated overview of the labour market: "
        "district counts, sector/trade coverage, shortage/oversupply tallies, "
        "demand/supply totals, sector breakdowns, district summaries, "
        "multi-year trend, key metric cards, and the top-5 critical shortage trades."
    ),
)
def get_national_overview(db: Session = Depends(get_db)) -> NationalOverview:
    # ── Taxonomy counts ────────────────────────────────────────────────────────
    total_districts = db.query(func.count(District.id)).scalar() or 0
    monitored_sectors = db.query(func.count(Sector.id)).scalar() or 0
    monitored_trades = db.query(func.count(Trade.id)).scalar() or 0

    # ── SkillGap aggregates for the reference year ─────────────────────────────
    gaps_2024 = db.query(SkillGap).filter(SkillGap.year == _OVERVIEW_YEAR).all()

    shortages_count = sum(1 for g in gaps_2024 if g.status == "SHORTAGE")
    oversupply_count = sum(1 for g in gaps_2024 if g.status == "OVERSUPPLY")
    balanced_count = sum(1 for g in gaps_2024 if g.status == "BALANCED")

    # Critical = urgency_tier in {"Critical", "High"}
    emerging_critical = sum(
        1 for g in gaps_2024 if g.urgency_tier in {"Critical", "High"}
    )

    avg_severity = (
        sum(g.severity_score for g in gaps_2024) / len(gaps_2024)
        if gaps_2024
        else 0.0
    )

    # ── Demand / Supply totals for reference year ──────────────────────────────
    total_demand: int = (
        db.query(func.sum(LabourDemand.estimated_total_demand))
        .filter(LabourDemand.year == _OVERVIEW_YEAR)
        .scalar()
        or 0
    )
    total_supply: int = (
        db.query(func.sum(TrainingSupply.effective_local_supply))
        .filter(TrainingSupply.year == _OVERVIEW_YEAR)
        .scalar()
        or 0
    )
    net_gap = total_demand - total_supply

    # ── Sector breakdown ───────────────────────────────────────────────────────
    sector_map: Dict[int, Dict[str, Any]] = {}
    for g in gaps_2024:
        sid = g.sector_id
        if sid not in sector_map:
            sector_obj = db.query(Sector).filter(Sector.id == sid).first()
            sector_map[sid] = {
                "sector_id": sid,
                "sector_name": sector_obj.name if sector_obj else f"Sector {sid}",
                "icon": sector_obj.icon if sector_obj else None,
                "demand_volume": 0,
                "supply_volume": 0,
                "net_gap": 0,
                "severity_scores": [],
                "statuses": [],
            }
        sector_map[sid]["demand_volume"] += g.demand_value
        sector_map[sid]["supply_volume"] += g.supply_value
        sector_map[sid]["net_gap"] += g.net_gap
        sector_map[sid]["severity_scores"].append(g.severity_score)
        sector_map[sid]["statuses"].append(g.status)

    sector_breakdown: List[SectorDistribution] = []
    for entry in sector_map.values():
        statuses = entry["statuses"]
        dominant = max(set(statuses), key=statuses.count) if statuses else "BALANCED"
        avg_sev = (
            sum(entry["severity_scores"]) / len(entry["severity_scores"])
            if entry["severity_scores"]
            else 0.0
        )
        sector_breakdown.append(
            SectorDistribution(
                sector_id=entry["sector_id"],
                sector_name=entry["sector_name"],
                icon=entry["icon"],
                demand_volume=entry["demand_volume"],
                supply_volume=entry["supply_volume"],
                net_gap=entry["net_gap"],
                status=dominant,
                severity_score=round(avg_sev, 2),
            )
        )
    sector_breakdown.sort(key=lambda x: x.severity_score, reverse=True)

    # ── District summaries ─────────────────────────────────────────────────────
    district_gap_map: Dict[int, Dict[str, Any]] = {}
    for g in gaps_2024:
        did = g.district_id
        if did not in district_gap_map:
            d_obj = db.query(District).filter(District.id == did).first()
            district_gap_map[did] = {
                "district_id": did,
                "district_name": d_obj.name if d_obj else f"District {did}",
                "latitude": d_obj.latitude if d_obj else None,
                "longitude": d_obj.longitude if d_obj else None,
                "total_demand": 0,
                "total_supply": 0,
                "net_gap": 0,
                "critical_shortages_count": 0,
                "oversupply_count": 0,
                "top_shortage_severity": -1.0,
                "top_shortage_trade": None,
                "severity_scores": [],
                "statuses": [],
            }
        dm = district_gap_map[did]
        dm["total_demand"] += g.demand_value
        dm["total_supply"] += g.supply_value
        dm["net_gap"] += g.net_gap
        dm["severity_scores"].append(g.severity_score)
        dm["statuses"].append(g.status)
        if g.status == "SHORTAGE" and g.urgency_tier in {"Critical", "High"}:
            dm["critical_shortages_count"] += 1
        if g.status == "OVERSUPPLY":
            dm["oversupply_count"] += 1
        if g.status == "SHORTAGE" and g.severity_score > dm["top_shortage_severity"]:
            dm["top_shortage_severity"] = g.severity_score
            t_obj = db.query(Trade).filter(Trade.id == g.trade_id).first()
            dm["top_shortage_trade"] = t_obj.name if t_obj else None

    district_summaries: List[DistrictSummaryItem] = []
    for dm in district_gap_map.values():
        statuses = dm["statuses"]
        dominant = max(set(statuses), key=statuses.count) if statuses else "BALANCED"
        avg_sev = (
            sum(dm["severity_scores"]) / len(dm["severity_scores"])
            if dm["severity_scores"]
            else 0.0
        )
        district_summaries.append(
            DistrictSummaryItem(
                district_id=dm["district_id"],
                district_name=dm["district_name"],
                latitude=dm["latitude"],
                longitude=dm["longitude"],
                total_demand=dm["total_demand"],
                total_supply=dm["total_supply"],
                net_gap=dm["net_gap"],
                critical_shortages_count=dm["critical_shortages_count"],
                oversupply_count=dm["oversupply_count"],
                top_shortage_trade=dm["top_shortage_trade"],
                status=dominant,
                severity_score=round(avg_sev, 2),
            )
        )
    district_summaries.sort(key=lambda x: x.severity_score, reverse=True)

    # ── Time-series trend (2019-2024) ──────────────────────────────────────────
    time_series_trend: List[Dict[str, Any]] = []
    for yr in _TIME_SERIES_YEARS:
        yr_demand: int = (
            db.query(func.sum(LabourDemand.estimated_total_demand))
            .filter(LabourDemand.year == yr)
            .scalar()
            or 0
        )
        yr_supply: int = (
            db.query(func.sum(TrainingSupply.effective_local_supply))
            .filter(TrainingSupply.year == yr)
            .scalar()
            or 0
        )
        time_series_trend.append(
            {
                "year": yr,
                "total_demand": yr_demand,
                "total_supply": yr_supply,
                "net_gap": yr_demand - yr_supply,
            }
        )

    # ── Top 5 critical shortage trades ────────────────────────────────────────
    top_critical_raw = (
        db.query(SkillGap)
        .filter(SkillGap.year == _OVERVIEW_YEAR, SkillGap.status == "SHORTAGE")
        .order_by(SkillGap.severity_score.desc())
        .limit(5)
        .all()
    )
    top_critical_trades: List[Dict[str, Any]] = []
    for g in top_critical_raw:
        d_obj = db.query(District).filter(District.id == g.district_id).first()
        s_obj = db.query(Sector).filter(Sector.id == g.sector_id).first()
        t_obj = db.query(Trade).filter(Trade.id == g.trade_id).first()
        top_critical_trades.append(
            {
                "district_name": d_obj.name if d_obj else f"District {g.district_id}",
                "sector_name": s_obj.name if s_obj else f"Sector {g.sector_id}",
                "trade_name": t_obj.name if t_obj else f"Trade {g.trade_id}",
                "demand": g.demand_value,
                "supply": g.supply_value,
                "net_gap": g.net_gap,
                "severity_score": g.severity_score,
                "urgency_tier": g.urgency_tier,
                "diagnostic_explanation": g.diagnostic_explanation,
            }
        )

    # ── Metric cards ───────────────────────────────────────────────────────────
    metric_cards: List[MetricCard] = [
        MetricCard(
            label="Total Labour Demand (2024)",
            value=f"{total_demand:,}",
            trend_direction="up",
            badge_variant="info",
            description="Estimated total skilled job openings across all monitored trades.",
        ),
        MetricCard(
            label="Total Training Supply (2024)",
            value=f"{total_supply:,}",
            trend_direction="neutral",
            badge_variant="primary",
            description="Certified passouts and effective skilled supply entering the market.",
        ),
        MetricCard(
            label="Net Labour Gap",
            value=f"{net_gap:,}",
            trend_direction="up" if net_gap > 0 else "down",
            badge_variant="danger" if net_gap > 0 else "success",
            description="Demand minus Supply. Positive = shortage; Negative = oversupply.",
        ),
        MetricCard(
            label="Shortage Trades",
            value=shortages_count,
            badge_variant="danger",
            description="Trades where demand significantly exceeds supply (gap ratio > 15 %).",
        ),
        MetricCard(
            label="Oversupply Trades",
            value=oversupply_count,
            badge_variant="warning",
            description="Trades where supply significantly exceeds demand (gap ratio < -15 %).",
        ),
        MetricCard(
            label="Balanced Trades",
            value=balanced_count,
            badge_variant="success",
            description="Trades with a healthy demand-supply equilibrium.",
        ),
        MetricCard(
            label="Average Severity Score",
            value=round(avg_severity, 1),
            badge_variant="warning" if avg_severity > 50 else "info",
            description="Mean skill gap severity across all trade-district pairs (0–100 scale).",
        ),
        MetricCard(
            label="Critical / High Urgency Trades",
            value=emerging_critical,
            badge_variant="danger",
            description="Trades classified as Critical or High urgency requiring immediate policy intervention.",
        ),
    ]

    return NationalOverview(
        total_districts=total_districts,
        monitored_sectors=monitored_sectors,
        monitored_trades=monitored_trades,
        current_shortage_trades_count=shortages_count,
        current_oversupply_trades_count=oversupply_count,
        balanced_trades_count=balanced_count,
        emerging_critical_shortages_count=emerging_critical,
        total_annual_demand=total_demand,
        total_annual_supply=total_supply,
        net_labour_gap=net_gap,
        average_severity_score=round(avg_severity, 2),
        metric_cards=metric_cards,
        sector_breakdown=sector_breakdown,
        district_summaries=district_summaries,
        top_critical_trades=top_critical_trades,
        time_series_trend=time_series_trend,
    )


# ── /api/states ────────────────────────────────────────────────────────────────
@router.get(
    "/states",
    response_model=List[StateItem],
    summary="List all states",
    description="Returns all states in the database along with their district count.",
)
def list_states(db: Session = Depends(get_db)) -> List[StateItem]:
    states = db.query(State).order_by(State.name).all()
    result: List[StateItem] = []
    for s in states:
        districts_count = (
            db.query(func.count(District.id))
            .filter(District.state_id == s.id)
            .scalar()
            or 0
        )
        result.append(
            StateItem(
                id=s.id,
                code=s.code,
                name=s.name,
                region=s.region,
                is_pilot=bool(s.is_pilot),
                districts_count=districts_count,
            )
        )
    return result


# ── /api/states/{state_id}/districts ──────────────────────────────────────────
@router.get(
    "/states/{state_id}/districts",
    response_model=List[DistrictItem],
    summary="Get districts for a state",
    description="Returns all districts belonging to the specified state.",
)
def list_districts_by_state(
    state_id: int, db: Session = Depends(get_db)
) -> List[DistrictItem]:
    state = db.query(State).filter(State.id == state_id).first()
    if state is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"State with id={state_id} not found.",
        )
    districts = (
        db.query(District)
        .filter(District.state_id == state_id)
        .order_by(District.name)
        .all()
    )
    return [
        DistrictItem(
            id=d.id,
            name=d.name,
            state_id=d.state_id,
            state_name=state.name,
            latitude=d.latitude,
            longitude=d.longitude,
            economic_tier=d.economic_tier,
            population_lakhs=d.population_lakhs,
        )
        for d in districts
    ]


# ── /api/sectors ───────────────────────────────────────────────────────────────
@router.get(
    "/sectors",
    response_model=List[SectorItem],
    summary="List all sectors",
    description="Returns all industry sectors tracked by SkillSetu AI.",
)
def list_sectors(db: Session = Depends(get_db)) -> List[SectorItem]:
    sectors = db.query(Sector).order_by(Sector.name).all()
    return [
        SectorItem(
            id=s.id,
            code=s.code,
            name=s.name,
            icon=s.icon,
            description=s.description,
            ssc_name=s.ssc_name,
        )
        for s in sectors
    ]


# ── /api/trades ────────────────────────────────────────────────────────────────
@router.get(
    "/trades",
    response_model=List[TradeItem],
    summary="List all trades",
    description=(
        "Returns all trades. Pass an optional ?sector_id=<id> query parameter "
        "to filter trades belonging to a specific sector."
    ),
)
def list_trades(
    sector_id: Optional[int] = Query(default=None, description="Filter by sector ID"),
    db: Session = Depends(get_db),
) -> List[TradeItem]:
    query = db.query(Trade)
    if sector_id is not None:
        sector = db.query(Sector).filter(Sector.id == sector_id).first()
        if sector is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sector with id={sector_id} not found.",
            )
        query = query.filter(Trade.sector_id == sector_id)
    trades = query.order_by(Trade.name).all()
    sector_names: Dict[int, str] = {}
    result: List[TradeItem] = []
    for t in trades:
        if t.sector_id not in sector_names:
            s_obj = db.query(Sector).filter(Sector.id == t.sector_id).first()
            sector_names[t.sector_id] = s_obj.name if s_obj else ""
        result.append(
            TradeItem(
                id=t.id,
                code=t.code,
                name=t.name,
                sector_id=t.sector_id,
                sector_name=sector_names[t.sector_id],
                nsqf_level=t.nsqf_level,
                duration_months=t.duration_months,
            )
        )
    return result


# ── /api/districts/{district_id}/trades ───────────────────────────────────────
@router.get(
    "/districts/{district_id}/trades",
    response_model=List[TradeItem],
    summary="Trades active in a district",
    description=(
        "Returns all trades that have at least one LabourDemand or TrainingSupply "
        "record in the given district."
    ),
)
def list_trades_by_district(
    district_id: int, db: Session = Depends(get_db)
) -> List[TradeItem]:
    district = db.query(District).filter(District.id == district_id).first()
    if district is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"District with id={district_id} not found.",
        )

    # Gather trade IDs that appear in demand OR supply for this district
    demand_trade_ids = {
        r[0]
        for r in db.query(LabourDemand.trade_id)
        .filter(LabourDemand.district_id == district_id)
        .distinct()
        .all()
    }
    supply_trade_ids = {
        r[0]
        for r in db.query(TrainingSupply.trade_id)
        .filter(TrainingSupply.district_id == district_id)
        .distinct()
        .all()
    }
    trade_ids = demand_trade_ids | supply_trade_ids

    if not trade_ids:
        return []

    trades = db.query(Trade).filter(Trade.id.in_(trade_ids)).order_by(Trade.name).all()
    sector_names: Dict[int, str] = {}
    result: List[TradeItem] = []
    for t in trades:
        if t.sector_id not in sector_names:
            s_obj = db.query(Sector).filter(Sector.id == t.sector_id).first()
            sector_names[t.sector_id] = s_obj.name if s_obj else ""
        result.append(
            TradeItem(
                id=t.id,
                code=t.code,
                name=t.name,
                sector_id=t.sector_id,
                sector_name=sector_names[t.sector_id],
                nsqf_level=t.nsqf_level,
                duration_months=t.duration_months,
            )
        )
    return result

