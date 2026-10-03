import numpy as np
import pandas as pd
from typing import Dict, Any, List
from app.config import settings

class DemandEngine:
    """
    Demand Index Engine:
    Aggregates and normalizes multi-source heterogeneous labour demand signals.
    
    Mathematical Formulation:
    -------------------------
    Let:
      - JP = Job Postings Count (normalized via Min-Max scale across district peer group)
      - HG = Hiring Growth Rate % (normalized via Sigmoid/Min-Max scale: 0 to 100)
      - GVA = Sector Gross Value Added Growth % (normalized: 0 to 100)
      - INV = Industrial Investment Inflows in Cr (normalized: 0 to 100)
    
    Demand Index (DI) = (w_jp * S_jp) + (w_hg * S_hg) + (w_gva * S_gva) + (w_inv * S_inv)
    Where weights sum to 1.0 (Configurable via backend settings).
    
    Estimated Total Demand Volume (DV) = JP + Vacancies + Base Headcount Expansions
    """
    
    def __init__(self):
        self.weights = {
            "job_postings": settings.DEMAND_WEIGHT_JOB_POSTINGS,
            "hiring_growth": settings.DEMAND_WEIGHT_HIRING_GROWTH,
            "gva_growth": settings.DEMAND_WEIGHT_SECTOR_GVA_GROWTH,
            "investments": settings.DEMAND_WEIGHT_INVESTMENT_INFLOWS
        }

    def compute_demand_index(
        self,
        job_postings: int,
        employer_vacancies: int,
        hiring_growth_pct: float,
        gva_growth_pct: float,
        investment_inflow_crores: float,
        max_benchmarks: Dict[str, float] = None
    ) -> Dict[str, Any]:
        """Calculate normalized demand index (0-100) and estimated demand volume."""
        
        benchmarks = max_benchmarks or {
            "max_postings": 5000.0,
            "max_hiring_growth": 40.0,
            "max_gva_growth": 20.0,
            "max_investments": 2500.0
        }
        
        # Sub-score calculations (clipped between 0 and 100)
        s_jp = np.clip((job_postings / max(benchmarks["max_postings"], 1.0)) * 100.0, 0.0, 100.0)
        s_hg = np.clip(((hiring_growth_pct + 10.0) / (benchmarks["max_hiring_growth"] + 10.0)) * 100.0, 0.0, 100.0)
        s_gva = np.clip(((gva_growth_pct + 5.0) / (benchmarks["max_gva_growth"] + 5.0)) * 100.0, 0.0, 100.0)
        s_inv = np.clip((investment_inflow_crores / max(benchmarks["max_investments"], 1.0)) * 100.0, 0.0, 100.0)
        
        demand_index = (
            self.weights["job_postings"] * s_jp +
            self.weights["hiring_growth"] * s_hg +
            self.weights["gva_growth"] * s_gva +
            self.weights["investments"] * s_inv
        )
        
        # Total demand volume is the sum of direct postings + unreported vacancies multiplier
        estimated_demand = int(round(job_postings + employer_vacancies + (investment_inflow_crores * 0.45)))
        
        return {
            "demand_index": round(float(demand_index), 2),
            "estimated_demand": max(estimated_demand, 10),
            "sub_scores": {
                "job_postings_score": round(float(s_jp), 2),
                "hiring_growth_score": round(float(s_hg), 2),
                "gva_growth_score": round(float(s_gva), 2),
                "investments_score": round(float(s_inv), 2)
            }
        }

demand_engine = DemandEngine()
