import numpy as np
from typing import Dict, Any
from app.config import settings

class SupplyEngine:
    """
    Supply Index Engine:
    Calculates transparent local training pipeline supply indicators from ITIs, Polytechnics,
    PMKVY centers, and state skill institutes.
    
    Mathematical Formulation:
    -------------------------
    Let:
      - SS = Sanctioned Seat Capacity (Score S_ss: 0 to 100)
      - EN = Enrolled Candidates / Intake (Score S_en: 0 to 100)
      - CP = Certified Passouts / Graduates (Score S_cp: 0 to 100)
      - LR = Local Placement & Retention Absorption Rate %
    
    Supply Index (SI) = (w_ss * S_ss) + (w_en * S_en) + (w_cp * S_cp)
    Where weights sum to 1.0.
    
    Effective Available Skilled Supply (ES) = CP * (LR / 100.0)
    """
    
    def __init__(self):
        self.weights = {
            "sanctioned_seats": settings.SUPPLY_WEIGHT_SANCTIONED_SEATS,
            "enrolments": settings.SUPPLY_WEIGHT_ENROLMENTS,
            "completions": settings.SUPPLY_WEIGHT_COMPLETIONS_PASSOUTS
        }

    def compute_supply_index(
        self,
        sanctioned_seats: int,
        enrolled: int,
        passouts: int,
        local_absorption_rate_pct: float,
        max_benchmarks: Dict[str, float] = None
    ) -> Dict[str, Any]:
        """Calculate normalized supply index (0-100) and effective local skilled supply."""
        
        benchmarks = max_benchmarks or {
            "max_seats": 4000.0,
            "max_enrolments": 3600.0,
            "max_passouts": 3200.0
        }
        
        s_ss = np.clip((sanctioned_seats / max(benchmarks["max_seats"], 1.0)) * 100.0, 0.0, 100.0)
        s_en = np.clip((enrolled / max(benchmarks["max_enrolments"], 1.0)) * 100.0, 0.0, 100.0)
        s_cp = np.clip((passouts / max(benchmarks["max_passouts"], 1.0)) * 100.0, 0.0, 100.0)
        
        supply_index = (
            self.weights["sanctioned_seats"] * s_ss +
            self.weights["enrolments"] * s_en +
            self.weights["completions"] * s_cp
        )
        
        # Effective local supply considers passouts adjusted for local retention rate
        effective_supply = int(round(passouts * (local_absorption_rate_pct / 100.0)))
        
        return {
            "supply_index": round(float(supply_index), 2),
            "effective_supply": max(effective_supply, 5),
            "sub_scores": {
                "seats_score": round(float(s_ss), 2),
                "enrolments_score": round(float(s_en), 2),
                "passouts_score": round(float(s_cp), 2)
            }
        }

supply_engine = SupplyEngine()
