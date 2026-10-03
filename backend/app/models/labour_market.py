from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base


class LabourDemand(Base):
    __tablename__ = "labour_demand"

    id = Column(Integer, primary_key=True, index=True)
    district_id = Column(Integer, ForeignKey("districts.id"), nullable=False)
    sector_id = Column(Integer, ForeignKey("sectors.id"), nullable=False)
    trade_id = Column(Integer, ForeignKey("trades.id"), nullable=False)
    year = Column(Integer, nullable=False)

    # Raw demand signals
    job_postings_count = Column(Integer, default=0)
    hiring_growth_rate_pct = Column(Float, default=0.0)
    gva_growth_pct = Column(Float, default=0.0)          # sector GVA growth rate
    investment_inflow_crores = Column(Float, default=0.0)

    # Calculated
    normalized_demand_index = Column(Float, default=0.0)   # 0-100
    estimated_total_demand = Column(Integer, default=0)    # incl. informal sector estimate

    is_synthetic = Column(Boolean, default=True)
    data_source = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    district = relationship("District", back_populates="demand_records")
    sector = relationship("Sector", back_populates="demand_records")
    trade = relationship("Trade", back_populates="demand_records")

    __table_args__ = (
        UniqueConstraint("district_id", "sector_id", "trade_id", "year", name="uq_demand_geo_trade_year"),
    )


class TrainingSupply(Base):
    __tablename__ = "training_supply"

    id = Column(Integer, primary_key=True, index=True)
    district_id = Column(Integer, ForeignKey("districts.id"), nullable=False)
    sector_id = Column(Integer, ForeignKey("sectors.id"), nullable=False)
    trade_id = Column(Integer, ForeignKey("trades.id"), nullable=False)
    year = Column(Integer, nullable=False)

    # Raw supply signals
    sanctioned_seats = Column(Integer, default=0)
    actual_enrolments = Column(Integer, default=0)
    passouts = Column(Integer, default=0)
    local_absorption_rate_pct = Column(Float, default=0.0)

    # Calculated
    effective_local_supply = Column(Integer, default=0)    # passouts × absorption_rate
    normalized_supply_index = Column(Float, default=0.0)   # 0-100

    is_synthetic = Column(Boolean, default=True)
    data_source = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    district = relationship("District", back_populates="supply_records")
    sector = relationship("Sector", back_populates="supply_records")
    trade = relationship("Trade", back_populates="supply_records")

    __table_args__ = (
        UniqueConstraint("district_id", "sector_id", "trade_id", "year", name="uq_supply_geo_trade_year"),
    )


class LabourIndicator(Base):
    """Macro labour indicators by District/Year (PLFS-aligned)."""
    __tablename__ = "labour_indicators"

    id = Column(Integer, primary_key=True, index=True)
    district_id = Column(Integer, ForeignKey("districts.id"), nullable=False)
    year = Column(Integer, nullable=False)
    unemployment_rate_pct = Column(Float, default=0.0)
    labour_force_participation_rate = Column(Float, default=0.0)
    female_workforce_participation_pct = Column(Float, default=0.0)
    outmigration_index = Column(Float, default=0.0)
    average_wage_inr = Column(Float, default=0.0)
    source_agency = Column(String(100), default="PLFS / State Statistical Directorate")
