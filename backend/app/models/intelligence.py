from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base


class Forecast(Base):
    __tablename__ = "forecasts"

    id = Column(Integer, primary_key=True, index=True)
    district_id = Column(Integer, ForeignKey("districts.id"), nullable=False)
    sector_id = Column(Integer, ForeignKey("sectors.id"), nullable=False)
    trade_id = Column(Integer, ForeignKey("trades.id"), nullable=False)
    forecast_year = Column(Integer, nullable=False)

    # Projections
    forecasted_demand = Column(Integer, nullable=False, default=0)
    forecasted_supply = Column(Integer, nullable=False, default=0)
    demand_lower_bound = Column(Integer, nullable=True)
    demand_upper_bound = Column(Integer, nullable=True)
    supply_lower_bound = Column(Integer, nullable=True)
    supply_upper_bound = Column(Integer, nullable=True)

    # Model metadata
    model_name = Column(String(100), default="GradientBoostingRegressor")
    confidence_score_pct = Column(Float, default=87.5)
    is_synthetic = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    district = relationship("District", back_populates="forecasts")
    sector = relationship("Sector", back_populates="forecasts")
    trade = relationship("Trade", back_populates="forecasts")

    __table_args__ = (
        UniqueConstraint(
            "district_id", "sector_id", "trade_id", "forecast_year", "model_name",
            name="uq_forecast_unit_year_model",
        ),
    )


class SkillGap(Base):
    __tablename__ = "skill_gaps"

    id = Column(Integer, primary_key=True, index=True)
    district_id = Column(Integer, ForeignKey("districts.id"), nullable=False)
    sector_id = Column(Integer, ForeignKey("sectors.id"), nullable=False)
    trade_id = Column(Integer, ForeignKey("trades.id"), nullable=False)
    year = Column(Integer, nullable=False)

    demand_value = Column(Integer, nullable=False, default=0)
    supply_value = Column(Integer, nullable=False, default=0)
    net_gap = Column(Integer, nullable=False, default=0)
    gap_ratio_pct = Column(Float, nullable=False, default=0.0)

    # Classification & Severity
    status = Column(String(30), nullable=False, default="BALANCED")
    severity_score = Column(Float, nullable=False, default=0.0)    # 0-100
    urgency_tier = Column(String(20), default="None")              # Critical|High|Medium|Low|None

    # Explanation
    diagnostic_explanation = Column(Text, nullable=True)
    policy_recommendation = Column(Text, nullable=True)

    is_forecast = Column(Boolean, default=False)
    is_synthetic = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    district = relationship("District", back_populates="skill_gaps")
    sector = relationship("Sector", back_populates="skill_gaps")
    trade = relationship("Trade", back_populates="skill_gaps")

    __table_args__ = (
        UniqueConstraint(
            "district_id", "sector_id", "trade_id", "year",
            name="uq_skill_gap_unit_year",
        ),
    )


class ModelRun(Base):
    __tablename__ = "model_runs"

    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(100), nullable=False)
    train_years = Column(String(50), nullable=True)    # e.g. "2019-2023"
    test_year = Column(Integer, nullable=True)

    # Evaluation metrics (on held-out test split)
    mae = Column(Float, nullable=True)
    rmse = Column(Float, nullable=True)
    mape = Column(Float, nullable=True)
    r2_score = Column(Float, nullable=True)

    feature_importances = Column(Text, nullable=True)  # JSON string
    is_primary = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)
    executed_at = Column(DateTime, default=datetime.utcnow)


class ScenarioRun(Base):
    __tablename__ = "scenario_runs"

    id = Column(Integer, primary_key=True, index=True)
    scenario_name = Column(String(150), nullable=True)
    district_id = Column(Integer, ForeignKey("districts.id"), nullable=False)
    sector_id = Column(Integer, ForeignKey("sectors.id"), nullable=False)
    trade_id = Column(Integer, ForeignKey("trades.id"), nullable=False)
    target_year = Column(Integer, nullable=False)

    # Interventions applied
    additional_seats = Column(Integer, default=0)
    intake_expansion_pct = Column(Float, default=0.0)
    demand_surge_pct = Column(Float, default=0.0)
    placement_boost_pct = Column(Float, default=0.0)

    # Baseline vs Scenario results
    baseline_gap = Column(Float, nullable=True)
    scenario_gap = Column(Float, nullable=True)
    baseline_status = Column(String(30), nullable=True)
    scenario_status = Column(String(30), nullable=True)
    baseline_severity = Column(Float, nullable=True)
    scenario_severity = Column(Float, nullable=True)

    policy_impact_summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class DatasetCoverage(Base):
    __tablename__ = "dataset_coverage"

    id = Column(Integer, primary_key=True, index=True)
    source_name = Column(String(150), nullable=False)
    source_url = Column(String(300), nullable=True)
    category = Column(String(100), nullable=True)           # Supply | Demand | Macro | Taxonomy
    years_covered = Column(String(50), nullable=True)
    states_covered = Column(String(200), nullable=True)
    districts_covered = Column(Integer, default=0)
    sectors_covered = Column(Integer, default=0)
    trades_covered = Column(Integer, default=0)
    record_count = Column(Integer, default=0)
    is_synthetic = Column(Boolean, default=True)
    last_updated = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
