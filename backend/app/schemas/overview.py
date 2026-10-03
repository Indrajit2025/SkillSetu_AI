from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class MetricCard(BaseModel):
    label: str
    value: Any
    change_pct: Optional[float] = None
    trend_direction: Optional[str] = None # "up", "down", "neutral"
    badge_variant: Optional[str] = "primary" # "danger", "warning", "success", "info"
    description: Optional[str] = None

class SectorDistribution(BaseModel):
    sector_id: int
    sector_name: str
    icon: Optional[str] = None
    demand_volume: int
    supply_volume: int
    net_gap: int
    status: str
    severity_score: float

class DistrictSummaryItem(BaseModel):
    district_id: int
    district_name: str
    latitude: Optional[float]
    longitude: Optional[float]
    total_demand: int
    total_supply: int
    net_gap: int
    critical_shortages_count: int
    oversupply_count: int
    top_shortage_trade: Optional[str] = None
    status: str
    severity_score: float

class NationalOverview(BaseModel):
    total_districts: int
    monitored_sectors: int
    monitored_trades: int
    current_shortage_trades_count: int
    current_oversupply_trades_count: int
    balanced_trades_count: int
    emerging_critical_shortages_count: int
    
    total_annual_demand: int
    total_annual_supply: int
    net_labour_gap: int
    average_severity_score: float
    
    metric_cards: List[MetricCard]
    sector_breakdown: List[SectorDistribution]
    district_summaries: List[DistrictSummaryItem]
    top_critical_trades: List[Dict[str, Any]]
    time_series_trend: List[Dict[str, Any]] # year by year aggregated demand vs supply
