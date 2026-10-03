from pydantic import BaseModel
from typing import List, Optional, Dict


class StateItem(BaseModel):
    id: int
    code: str
    name: str
    region: Optional[str] = None
    is_pilot: bool
    districts_count: int = 0

    model_config = {"from_attributes": True}


class DistrictItem(BaseModel):
    id: int
    name: str
    state_id: int
    state_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    economic_tier: Optional[str] = None
    population_lakhs: Optional[float] = None

    model_config = {"from_attributes": True}


class SectorItem(BaseModel):
    id: int
    code: str
    name: str
    icon: Optional[str] = None
    description: Optional[str] = None
    ssc_name: Optional[str] = None

    model_config = {"from_attributes": True}


class TradeItem(BaseModel):
    id: int
    code: str
    name: str
    sector_id: int
    sector_name: Optional[str] = None
    nsqf_level: Optional[int] = None
    duration_months: Optional[int] = None

    model_config = {"from_attributes": True}


class DemandSeriesPoint(BaseModel):
    id: Optional[int] = None
    district_id: int
    sector_id: int
    trade_id: int
    year: int
    job_postings_count: int = 0
    hiring_growth_rate_pct: float = 0.0
    gva_growth_pct: float = 0.0
    investment_inflow_crores: float = 0.0
    normalized_demand_index: float = 0.0
    estimated_total_demand: int = 0
    is_synthetic: bool = True


class SupplySeriesPoint(BaseModel):
    id: Optional[int] = None
    district_id: int
    sector_id: int
    trade_id: int
    year: int
    sanctioned_seats: int = 0
    actual_enrolments: int = 0
    passouts: int = 0
    local_absorption_rate_pct: float = 0.0
    effective_local_supply: int = 0
    normalized_supply_index: float = 0.0
    is_synthetic: bool = True


class MarketDetailsResponse(BaseModel):
    district_name: str
    sector_name: str
    trade_name: str
    demand_series: List[DemandSeriesPoint]
    supply_series: List[SupplySeriesPoint]
    demand_weight_config: Dict[str, float]
    supply_weight_config: Dict[str, float]
