"""
skill_gap_service.py
--------------------
Skill gap calculation and classification service for SkillSetu AI.

Classification logic
--------------------
  gap_ratio = (demand - supply) / demand   [positive => shortage]

  STATUS:
    gap_ratio > SHORTAGE_THRESHOLD     -> 'SHORTAGE'
    gap_ratio < OVERSUPPLY_THRESHOLD   -> 'OVERSUPPLY'
    otherwise                          -> 'BALANCED'

  SEVERITY_SCORE (0 – 100):
    abs(gap_ratio_pct) * scaling_factor, clamped to [0, 100]

  URGENCY_TIER:
    severity_score > 80  -> 'Critical'
    severity_score > 60  -> 'High'
    severity_score > 40  -> 'Medium'
    severity_score > 20  -> 'Low'
    otherwise            -> 'None'
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from app.config import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Defaults (overridable via settings)
# ---------------------------------------------------------------------------

_DEFAULT_SHORTAGE_THRESHOLD:   float = 0.10   # 10 % shortfall
_DEFAULT_OVERSUPPLY_THRESHOLD: float = -0.05  # 5 % oversupply
_DEFAULT_SEVERITY_SCALE:       float = 1.0    # multiplier on |gap_ratio_pct|

# Urgency tier band boundaries (severity_score)
_TIER_CRITICAL: float = 80.0
_TIER_HIGH:     float = 60.0
_TIER_MEDIUM:   float = 40.0
_TIER_LOW:      float = 20.0


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------

class SkillGapService:
    """
    Stateless service for classifying workforce skill gaps.

    Usage
    -----
    from app.services.skill_gap_service import skill_gap_service

    result = skill_gap_service.classify_gap(demand=5000, supply=3800)
    """

    def __init__(self) -> None:
        # Pull configurable defaults from application settings if present
        self._shortage_threshold:   float = getattr(
            settings, "SHORTAGE_THRESHOLD", _DEFAULT_SHORTAGE_THRESHOLD
        )
        self._oversupply_threshold: float = getattr(
            settings, "OVERSUPPLY_THRESHOLD", _DEFAULT_OVERSUPPLY_THRESHOLD
        )
        self._severity_scale:       float = getattr(
            settings, "SEVERITY_SCALE", _DEFAULT_SEVERITY_SCALE
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _safe_gap_ratio(demand: float, supply: float) -> float:
        """
        gap_ratio = (demand - supply) / demand.
        Returns 0.0 when demand is zero to avoid ZeroDivisionError.
        """
        if demand == 0:
            logger.warning(
                "classify_gap called with demand=0; gap_ratio set to 0."
            )
            return 0.0
        return (demand - supply) / demand

    @staticmethod
    def _urgency_tier(severity_score: float) -> str:
        """Map a severity score to a human-readable urgency tier label."""
        if severity_score > _TIER_CRITICAL:
            return "Critical"
        if severity_score > _TIER_HIGH:
            return "High"
        if severity_score > _TIER_MEDIUM:
            return "Medium"
        if severity_score > _TIER_LOW:
            return "Low"
        return "None"

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def classify_gap(
        self,
        demand: float,
        supply: float,
        settings_thresholds: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Classify the skill gap between workforce demand and supply.

        Parameters
        ----------
        demand              : absolute demand figure (seats / workers required)
        supply              : absolute supply figure (available trained workers)
        settings_thresholds : optional dict to override thresholds at call time.
            Recognised keys:
              - 'shortage_threshold'   (float)
              - 'oversupply_threshold' (float)
              - 'severity_scale'       (float)

        Returns
        -------
        dict with keys:
          status          : 'SHORTAGE' | 'OVERSUPPLY' | 'BALANCED'
          severity_score  : float in [0, 100]
          urgency_tier    : 'Critical' | 'High' | 'Medium' | 'Low' | 'None'
          gap_ratio_pct   : float (percentage, e.g. 15.3 means 15.3 % shortage)
          net_gap         : float (demand – supply, positive => shortage)
        """
        # Allow per-call threshold overrides
        shortage_threshold   = self._shortage_threshold
        oversupply_threshold = self._oversupply_threshold
        severity_scale       = self._severity_scale

        if settings_thresholds:
            shortage_threshold   = float(
                settings_thresholds.get("shortage_threshold",   shortage_threshold)
            )
            oversupply_threshold = float(
                settings_thresholds.get("oversupply_threshold", oversupply_threshold)
            )
            severity_scale       = float(
                settings_thresholds.get("severity_scale",       severity_scale)
            )

        demand = float(demand)
        supply = float(supply)
        net_gap = demand - supply

        gap_ratio     = self._safe_gap_ratio(demand, supply)
        gap_ratio_pct = gap_ratio * 100.0  # convert to percentage

        # --- Status classification ---
        if gap_ratio > shortage_threshold:
            status = "SHORTAGE"
        elif gap_ratio < oversupply_threshold:
            status = "OVERSUPPLY"
        else:
            status = "BALANCED"

        # --- Severity score: 0 – 100 ---
        severity_score = min(abs(gap_ratio_pct) * severity_scale, 100.0)

        # --- Urgency tier ---
        urgency_tier = self._urgency_tier(severity_score)

        result: Dict[str, Any] = {
            "status":         status,
            "severity_score": round(severity_score, 2),
            "urgency_tier":   urgency_tier,
            "gap_ratio_pct":  round(gap_ratio_pct, 4),
            "net_gap":        round(net_gap, 2),
        }

        logger.debug(
            "classify_gap | demand=%.0f supply=%.0f -> status=%s severity=%.1f tier=%s",
            demand, supply, status, severity_score, urgency_tier,
        )

        return result

    def bulk_classify(
        self,
        pairs: list[Dict[str, float]],
        settings_thresholds: Optional[Dict[str, Any]] = None,
    ) -> list[Dict[str, Any]]:
        """
        Classify multiple demand/supply pairs in one call.

        Parameters
        ----------
        pairs               : list of {'demand': float, 'supply': float}
        settings_thresholds : shared threshold overrides applied to all pairs

        Returns
        -------
        List of classify_gap result dicts.
        """
        return [
            self.classify_gap(
                demand=p["demand"],
                supply=p["supply"],
                settings_thresholds=settings_thresholds,
            )
            for p in pairs
        ]


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------

skill_gap_service: SkillGapService = SkillGapService()
