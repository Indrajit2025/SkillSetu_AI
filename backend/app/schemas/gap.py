from pydantic import BaseModel
from typing import List, Optional


class SkillGapItem(BaseModel):
    id: Optional[int] = None
    district_id: int
    district_name: str = ""
    sector_id: int
    sector_name: str = ""
    trade_id: int
    trade_name: str = ""
    year: int
    demand_value: int = 0
    supply_value: int = 0
    net_gap: int = 0
    gap_ratio_pct: float = 0.0
    status: str = "BALANCED"         # SHORTAGE | BALANCED | OVERSUPPLY
    severity_score: float = 0.0      # 0 - 100
    urgency_tier: str = "None"       # Critical | High | Medium | Low | None
    diagnostic_explanation: str = ""
    is_forecast: bool = False
    is_synthetic: bool = True


class GapMatrixResponse(BaseModel):
    total_records: int
    shortages: int
    oversupply: int
    balanced: int
    items: List[SkillGapItem]


class RankedTradeItem(BaseModel):
    rank: int
    district_id: int
    sector_id: int
    trade_id: int
    district_name: str = ""
    sector_name: str = ""
    trade_name: str = ""
    year: int
    status: str
    severity_score: float
    urgency_tier: str
    net_gap: int
    gap_ratio_pct: float
    diagnostic_explanation: str = ""


class RankingsResponse(BaseModel):
    year: Optional[int] = None
    top_shortages: List[RankedTradeItem]
    top_oversupply: List[RankedTradeItem]
    near_balanced: List[RankedTradeItem]
