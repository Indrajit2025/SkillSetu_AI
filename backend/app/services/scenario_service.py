"""
scenario_service.py
-------------------
What-If scenario simulation service for SkillSetu AI.

Responsibilities
----------------
  1. Apply user-defined scenario adjustments to baseline demand/supply.
  2. Classify the resulting gap using SkillGapService.
  3. Build a year-by-year comparison timeline (2024 – 2028).
  4. Generate a human-readable policy_impact_summary.

Adjustments applied
-------------------
  scenario_supply = baseline_supply
                    + additional_seats
                    + int(baseline_supply * intake_expansion_pct / 100)

  scenario_demand = int(baseline_demand * (1 + demand_surge_pct / 100))

  effective_absorption applies placement_boost to reduce effective net gap.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from app.schemas.scenario import (
    ScenarioMetricPair,
    ScenarioSimulationRequest,
    ScenarioSimulationResult,
)
from app.services.skill_gap_service import skill_gap_service

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_TIMELINE_START_YEAR: int = 2024
_TIMELINE_END_YEAR:   int = 2028

# Decay factor applied to scenario adjustments beyond the first year
# (adjustments are assumed to have diminishing incremental impact each year).
_ADJUSTMENT_DECAY: float = 0.85


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------

class ScenarioService:
    """
    What-If scenario simulation engine.

    Usage
    -----
    from app.services.scenario_service import scenario_service

    result = scenario_service.run_simulation(
        baseline_demand=5000,
        baseline_supply=3800,
        request=scenario_request,
        district_name="Pune",
        sector_name="IT & ITES",
        trade_name="Data Analyst",
        year_forecasts=[...],
    )
    """

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _apply_adjustments(
        baseline_demand: float,
        baseline_supply: float,
        additional_seats: int,
        intake_expansion_pct: float,
        demand_surge_pct: float,
        placement_boost_pct: float,
        decay_factor: float = 1.0,
    ) -> Dict[str, float]:
        """
        Compute scenario-adjusted demand, supply, and effective absorption.

        Parameters
        ----------
        baseline_demand       : original demand value
        baseline_supply       : original supply value
        additional_seats      : absolute additional training seats
        intake_expansion_pct  : % expansion in institutional intake
        demand_surge_pct      : % increase in market demand
        placement_boost_pct   : % improvement in placement / absorption rate
        decay_factor          : how much the adjustments compound over time (0–1)

        Returns
        -------
        dict with: scenario_supply, scenario_demand, effective_supply, net_gap
        """
        scaled_add_seats     = int(additional_seats * decay_factor)
        scaled_expansion_pct = intake_expansion_pct * decay_factor

        scenario_supply: float = (
            baseline_supply
            + scaled_add_seats
            + int(baseline_supply * scaled_expansion_pct / 100)
        )

        scenario_demand: float = int(
            baseline_demand * (1 + (demand_surge_pct * decay_factor) / 100)
        )

        # Placement boost increases effective absorbed supply
        placement_multiplier: float = 1 + placement_boost_pct / 100
        effective_supply: float = scenario_supply * placement_multiplier

        net_gap: float = scenario_demand - effective_supply

        return {
            "scenario_supply":   round(scenario_supply, 2),
            "scenario_demand":   round(scenario_demand, 2),
            "effective_supply":  round(effective_supply, 2),
            "net_gap":           round(net_gap, 2),
        }

    @staticmethod
    def _get_year_forecast(
        year_forecasts: List[Any],
        target_year: int,
    ) -> Optional[Any]:
        """Return the ForecastPoint for a specific year, or None."""
        for fp in year_forecasts:
            yr = getattr(fp, "year", None) or (fp.get("year") if isinstance(fp, dict) else None)
            if yr == target_year:
                return fp
        return None

    @staticmethod
    def _extract_forecast_values(
        fp: Optional[Any],
        baseline_demand: float,
        baseline_supply: float,
    ) -> tuple[float, float]:
        """
        Extract demand/supply values from a ForecastPoint (dataclass or dict).
        Falls back to the provided baseline values if fp is None.
        """
        if fp is None:
            return baseline_demand, baseline_supply
        if isinstance(fp, dict):
            return (
                float(fp.get("predicted_demand", baseline_demand)),
                float(fp.get("predicted_supply", baseline_supply)),
            )
        return (
            float(getattr(fp, "predicted_demand", baseline_demand)),
            float(getattr(fp, "predicted_supply", baseline_supply)),
        )

    def _generate_policy_impact_summary(
        self,
        district_name:       str,
        sector_name:         str,
        trade_name:          str,
        baseline_gap_result: Dict[str, Any],
        scenario_gap_result: Dict[str, Any],
        request:             ScenarioSimulationRequest,
        delta_net_gap:       float,
        delta_severity:      float,
    ) -> str:
        """
        Produce a concise human-readable policy impact narrative.
        """
        baseline_status  = baseline_gap_result["status"]
        scenario_status  = scenario_gap_result["status"]
        baseline_tier    = baseline_gap_result["urgency_tier"]
        scenario_tier    = scenario_gap_result["urgency_tier"]

        improvements: List[str] = []
        if request.additional_seats > 0:
            improvements.append(
                f"adding {request.additional_seats:,} training seats"
            )
        if request.intake_expansion_pct > 0:
            improvements.append(
                f"expanding institutional intake by {request.intake_expansion_pct:.1f}%"
            )
        if request.placement_boost_pct > 0:
            improvements.append(
                f"boosting placement rates by {request.placement_boost_pct:.1f}%"
            )

        demand_note = ""
        if request.demand_surge_pct != 0:
            direction   = "increase" if request.demand_surge_pct > 0 else "decrease"
            demand_note = (
                f" Market demand is projected to {direction} by "
                f"{abs(request.demand_surge_pct):.1f}%."
            )

        policy_text = ", ".join(improvements) if improvements else "no supply-side interventions"

        status_change = (
            f"from {baseline_status} (Urgency: {baseline_tier}) "
            f"to {scenario_status} (Urgency: {scenario_tier})"
        )

        gap_direction = "reduced" if delta_net_gap < 0 else "increased"
        gap_abs       = abs(round(delta_net_gap, 0))
        severity_dir  = "improved" if delta_severity < 0 else "worsened"

        summary = (
            f"In {district_name} – {sector_name} ({trade_name}): {policy_text.capitalize()} "
            f"shifts the skill gap classification {status_change}.{demand_note} "
            f"Net gap {gap_direction} by {gap_abs:,.0f} units, and severity score "
            f"{severity_dir} by {abs(delta_severity):.1f} points. "
            f"Scenario description: '{request.scenario_name}'."
        )
        return summary

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run_simulation(
        self,
        baseline_demand: float,
        baseline_supply: float,
        request:         ScenarioSimulationRequest,
        district_name:   str,
        sector_name:     str,
        trade_name:      str,
        year_forecasts:  List[Any],
    ) -> ScenarioSimulationResult:
        """
        Run a What-If scenario simulation.

        Parameters
        ----------
        baseline_demand : current-year absolute demand
        baseline_supply : current-year absolute supply
        request         : ScenarioSimulationRequest (adjustments + metadata)
        district_name   : display name for the district
        sector_name     : display name for the sector
        trade_name      : display name for the trade/occupation
        year_forecasts  : list of ForecastPoint objects (or dicts) for 2024-2028

        Returns
        -------
        ScenarioSimulationResult
        """
        logger.info(
            "run_simulation | scenario='%s' district='%s' sector='%s' trade='%s'",
            request.scenario_name, district_name, sector_name, trade_name,
        )

        # --- Baseline gap (current year) ---
        baseline_gap = skill_gap_service.classify_gap(
            demand=baseline_demand,
            supply=baseline_supply,
        )

        # --- Scenario gap (current year, no decay) ---
        adj = self._apply_adjustments(
            baseline_demand=baseline_demand,
            baseline_supply=baseline_supply,
            additional_seats=request.additional_seats,
            intake_expansion_pct=request.intake_expansion_pct,
            demand_surge_pct=request.demand_surge_pct,
            placement_boost_pct=request.placement_boost_pct,
            decay_factor=1.0,
        )

        scenario_gap = skill_gap_service.classify_gap(
            demand=adj["scenario_demand"],
            supply=adj["effective_supply"],
        )

        # --- Year-by-year comparison timeline ---
        timeline: List[ScenarioMetricPair] = []
        timeline_years = list(range(_TIMELINE_START_YEAR, _TIMELINE_END_YEAR + 1))

        for idx, year in enumerate(timeline_years):
            fp = self._get_year_forecast(year_forecasts, year)
            yr_demand, yr_supply = self._extract_forecast_values(
                fp, baseline_demand, baseline_supply
            )

            # Decay factor: adjustments taper off in future years
            decay = _ADJUSTMENT_DECAY ** idx

            yr_adj = self._apply_adjustments(
                baseline_demand=yr_demand,
                baseline_supply=yr_supply,
                additional_seats=request.additional_seats,
                intake_expansion_pct=request.intake_expansion_pct,
                demand_surge_pct=request.demand_surge_pct,
                placement_boost_pct=request.placement_boost_pct,
                decay_factor=decay,
            )

            yr_baseline_gap = skill_gap_service.classify_gap(
                demand=yr_demand,
                supply=yr_supply,
            )
            yr_scenario_gap = skill_gap_service.classify_gap(
                demand=yr_adj["scenario_demand"],
                supply=yr_adj["effective_supply"],
            )

            timeline.append(
                ScenarioMetricPair(
                    year=year,
                    baseline_demand=round(yr_demand, 2),
                    baseline_supply=round(yr_supply, 2),
                    scenario_demand=yr_adj["scenario_demand"],
                    scenario_supply=yr_adj["scenario_supply"],
                    effective_scenario_supply=yr_adj["effective_supply"],
                    baseline_net_gap=yr_baseline_gap["net_gap"],
                    scenario_net_gap=yr_scenario_gap["net_gap"],
                    baseline_status=yr_baseline_gap["status"],
                    scenario_status=yr_scenario_gap["status"],
                    baseline_severity=yr_baseline_gap["severity_score"],
                    scenario_severity=yr_scenario_gap["severity_score"],
                    baseline_urgency_tier=yr_baseline_gap["urgency_tier"],
                    scenario_urgency_tier=yr_scenario_gap["urgency_tier"],
                )
            )

        # --- Policy impact summary ---
        delta_net_gap  = scenario_gap["net_gap"]  - baseline_gap["net_gap"]
        delta_severity = scenario_gap["severity_score"] - baseline_gap["severity_score"]

        policy_summary = self._generate_policy_impact_summary(
            district_name=district_name,
            sector_name=sector_name,
            trade_name=trade_name,
            baseline_gap_result=baseline_gap,
            scenario_gap_result=scenario_gap,
            request=request,
            delta_net_gap=delta_net_gap,
            delta_severity=delta_severity,
        )

        return ScenarioSimulationResult(
            scenario_name=request.scenario_name,
            district_name=district_name,
            sector_name=sector_name,
            trade_name=trade_name,
            # Current-year snapshot
            baseline_demand=round(baseline_demand, 2),
            baseline_supply=round(baseline_supply, 2),
            scenario_demand=adj["scenario_demand"],
            scenario_supply=adj["scenario_supply"],
            effective_scenario_supply=adj["effective_supply"],
            # Gap classifications
            baseline_status=baseline_gap["status"],
            scenario_status=scenario_gap["status"],
            baseline_severity_score=baseline_gap["severity_score"],
            scenario_severity_score=scenario_gap["severity_score"],
            baseline_urgency_tier=baseline_gap["urgency_tier"],
            scenario_urgency_tier=scenario_gap["urgency_tier"],
            baseline_net_gap=baseline_gap["net_gap"],
            scenario_net_gap=scenario_gap["net_gap"],
            # Deltas
            delta_net_gap=round(delta_net_gap, 2),
            delta_severity_score=round(delta_severity, 2),
            # Timeline
            comparison_timeline=timeline,
            # Narrative
            policy_impact_summary=policy_summary,
        )


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------

scenario_service: ScenarioService = ScenarioService()
