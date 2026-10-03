"""
Unit & Integration Test Suite for SkillSetu AI (SIH PS 26246)
Tests database seeding, authentication, overview aggregates, forecasting, and scenario simulator.
"""
import unittest
from fastapi.testclient import TestClient

from app.main import app
from app.database import SessionLocal
from app.models.geography import State, District
from app.models.taxonomy import Sector, Trade
from app.services.demand_engine import demand_engine
from app.services.supply_engine import supply_engine
from app.services.skill_gap_service import skill_gap_service


class TestSkillSetuEngines(unittest.TestCase):
    def test_demand_engine_calculation(self):
        """Verify DemandEngine normalizes and weights 4 signals deterministically."""
        result = demand_engine.compute_demand_index(
            job_postings=2500,
            employer_vacancies=1800,
            hiring_growth_pct=15.0,
            gva_growth_pct=10.0,
            investment_inflow_crores=50.0,
        )
        self.assertGreaterEqual(result["demand_index"], 0.0)
        self.assertLessEqual(result["demand_index"], 100.0)

    def test_supply_engine_calculation(self):
        """Verify SupplyEngine calculates effective local supply and index."""
        result = supply_engine.compute_supply_index(
            sanctioned_seats=400,
            enrolled=350,
            passouts=300,
            local_absorption_rate_pct=50.0,
        )
        self.assertEqual(result["effective_supply"], 150)
        self.assertGreaterEqual(result["supply_index"], 0.0)
        self.assertLessEqual(result["supply_index"], 100.0)

    def test_skill_gap_classification(self):
        """Verify shortage, oversupply, and balanced classification logic."""
        shortage = skill_gap_service.classify_gap(demand=5000, supply=1000)
        self.assertEqual(shortage["status"], "SHORTAGE")
        self.assertGreater(shortage["severity_score"], 50.0)

        oversupply = skill_gap_service.classify_gap(demand=1000, supply=5000)
        self.assertEqual(oversupply["status"], "OVERSUPPLY")

        balanced = skill_gap_service.classify_gap(demand=1000, supply=1020)
        self.assertEqual(balanced["status"], "BALANCED")


class TestSkillSetuAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_health_check(self):
        res = self.client.get("/health")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["status"], "healthy")

    def test_overview_endpoint(self):
        res = self.client.get("/api/overview")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["total_districts"], 30)
        self.assertGreater(data["total_annual_demand"], 0)
        self.assertEqual(len(data["metric_cards"]), 8)

    def test_states_endpoint(self):
        res = self.client.get("/api/states")
        self.assertEqual(res.status_code, 200)
        states = res.json()
        self.assertGreaterEqual(len(states), 1)
        pilot = next((s for s in states if s["is_pilot"]), None)
        self.assertIsNotNone(pilot)
        self.assertEqual(pilot["name"], "Odisha")

    def test_login_success(self):
        res = self.client.post("/api/auth/login", json={
            "email": "analyst@odisha.gov.in",
            "password": "Analyst@123"
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["token_type"], "bearer")
        self.assertIn("access_token", data)
        self.assertEqual(data["user"]["role"], "analyst")

    def test_login_failure(self):
        res = self.client.post("/api/auth/login", json={
            "email": "analyst@odisha.gov.in",
            "password": "WrongPassword999"
        })
        self.assertEqual(res.status_code, 401)

    def test_scenario_simulator(self):
        payload = {
            "scenario_name": "Test Simulation",
            "district_id": 1,
            "sector_id": 1,
            "trade_id": 1,
            "target_year": 2026,
            "additional_seats": 500,
            "intake_expansion_pct": 15.0,
            "demand_surge_pct": 5.0,
            "placement_boost_pct": 10.0
        }
        res = self.client.post("/api/scenarios", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("baseline_demand", data)
        self.assertIn("scenario_demand", data)
        self.assertIn("policy_impact_summary", data)
        self.assertEqual(len(data["comparison_timeline"]), 5)

    def test_model_evaluation(self):
        res = self.client.get("/api/model-evaluation")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertGreaterEqual(len(data["models"]), 3)
        primary = next((m for m in data["models"] if m["is_primary_model"]), None)
        self.assertIsNotNone(primary)
        self.assertEqual(primary["model_name"], "GradientBoostingRegressor")


if __name__ == "__main__":
    unittest.main()
