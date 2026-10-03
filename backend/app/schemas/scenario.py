from pydantic import BaseModel, Field
from typing import Optional, List, Any


class ScenarioSimulationRequest(BaseModel):
    scenario_name: str = "Policy Intervention Simulation"
    district_id: int
    sector_id: int
    trade_id: int
    target_year: int = 2026

    # Intervention knobs
    additional_seats: int = Field(default=0, description="Add new physical training seats")
    intake_expansion_pct: float = Field(default=0.0, description="Percentage boost to institute intake")
    demand_surge_pct: float = Field(default=0.0, description="Simulate demand surge/decline in %")
    placement_boost_pct: float = Field(default=0.0, description="Improvement in local retention/absorption rate")


class ScenarioMetricPair(BaseModel):
    """Year-by-year comparison row in the simulation timeline."""
    year: int
    baseline_demand: float
    baseline_supply: float
    scenario_demand: float
    scenario_supply: float
    effective_scenario_supply: float
    baseline_net_gap: float
    scenario_net_gap: float
    baseline_status: str
    scenario_status: str
    baseline_severity: float
    scenario_severity: float
    baseline_urgency_tier: str
    scenario_urgency_tier: str


class ScenarioSimulationResult(BaseModel):
    """Full result of a What-If scenario simulation."""
    scenario_name: str
    district_name: str
    sector_name: str
    trade_name: str

    # Current-year baseline values
    baseline_demand: float
    baseline_supply: float

    # Current-year scenario values (after interventions)
    scenario_demand: float
    scenario_supply: float
    effective_scenario_supply: float

    # Gap classifications — baseline
    baseline_status: str
    baseline_severity_score: float
    baseline_urgency_tier: str
    baseline_net_gap: float

    # Gap classifications — scenario
    scenario_status: str
    scenario_severity_score: float
    scenario_urgency_tier: str
    scenario_net_gap: float

    # Deltas
    delta_net_gap: float
    delta_severity_score: float

    # Year-by-year comparison (2024-2028)
    comparison_timeline: List[ScenarioMetricPair]

    # Narrative
    policy_impact_summary: str
