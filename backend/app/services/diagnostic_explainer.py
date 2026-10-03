from typing import Dict, Any

class DiagnosticExplainer:
    """
    Mathematical Diagnostic Engine:
    Inspects multi-year feature vectors (demand acceleration, seat utilization, 
    completion rates, GVA momentum) to synthesize human-readable, auditable
    policy explanations for why a skill gap exists.
    """
    
    @staticmethod
    def explain_skill_gap(
        demand_val: int,
        supply_val: int,
        demand_growth_pct: float,
        seat_utilization_pct: float,
        passout_rate_pct: float,
        gva_growth_pct: float,
        trade_name: str,
        district_name: str
    ) -> Dict[str, str]:
        
        net_gap = demand_val - supply_val
        gap_pct = (net_gap / max(demand_val + supply_val, 1)) * 100.0
        
        reasons = []
        recommendations = []
        
        # 1. Shortage Diagnostics
        if net_gap > 0 and gap_pct > 15.0:
            if demand_growth_pct > 10.0:
                reasons.append(f"Demand is accelerating rapidly (+{demand_growth_pct:.1f}% YoY) due to industrial growth")
            else:
                reasons.append("Steady demand outpaces current local intake capacity")
                
            if seat_utilization_pct > 90.0:
                reasons.append(f"Training facilities are near maximum capacity ({seat_utilization_pct:.1f}% seat occupancy)")
                recommendations.append(f"Sanction 15-25% additional seats in {district_name} technical institutes")
            elif seat_utilization_pct < 65.0:
                reasons.append(f"Low enrolment conversion despite high industry demand ({seat_utilization_pct:.1f}% seat utilization)")
                recommendations.append(f"Launch student mobilization and career awareness campaigns for {trade_name}")
                
            if passout_rate_pct < 75.0:
                reasons.append(f"High dropout rate during training pipeline ({passout_rate_pct:.1f}% passout rate)")
                recommendations.append("Strengthen practical lab infrastructure to improve curriculum completion")
                
            if gva_growth_pct > 8.0:
                reasons.append(f"Sector GVA momentum (+{gva_growth_pct:.1f}%) driving additional unmapped hiring")
                
            explanation = f"Deficit in {trade_name} ({net_gap:,} workers): " + "; ".join(reasons) + "."
            policy_rec = "Policy Action: " + ("; ".join(recommendations) if recommendations else "Expand sanctioned training quotas and partner with local employers.")
            
        # 2. Oversupply Diagnostics
        elif net_gap < 0 and gap_pct < -15.0:
            surplus = abs(net_gap)
            reasons.append(f"Annual certified passouts ({supply_val:,}) exceed local industry absorption ({demand_val:,})")
            
            if demand_growth_pct < 2.0:
                reasons.append(f"Stagnant hiring momentum ({demand_growth_pct:.1f}% YoY) in {district_name}")
                
            explanation = f"Oversupply in {trade_name} (+{surplus:,} surplus candidates): " + "; ".join(reasons) + "."
            policy_rec = f"Policy Action: Rationalize batch sizes for {trade_name} and reallocate training vouchers toward high-deficit adjacent sectors."
            
        # 3. Balanced Diagnostics
        else:
            explanation = f"Demand and local training supply are in equilibrium ({demand_val:,} demand vs {supply_val:,} supply). Seat intake matches current market throughput."
            policy_rec = "Policy Action: Maintain existing seat allocations; continuously update NSQF curriculum to sustain industry alignment."
            
        return {
            "diagnostic_explanation": explanation,
            "policy_recommendation": policy_rec
        }

diagnostic_explainer = DiagnosticExplainer()
