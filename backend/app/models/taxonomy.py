from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Sector(Base):
    __tablename__ = "sectors"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, index=True, nullable=False)   # e.g. "SEC_IT"
    name = Column(String(150), unique=True, nullable=False)              # e.g. "IT & Digital Services"
    icon = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    ssc_name = Column(String(200), nullable=True)                        # Sector Skill Council name

    trades = relationship("Trade", back_populates="sector", cascade="all, delete-orphan")
    demand_records = relationship("LabourDemand", back_populates="sector", cascade="all, delete-orphan")
    supply_records = relationship("TrainingSupply", back_populates="sector", cascade="all, delete-orphan")
    forecasts = relationship("Forecast", back_populates="sector", cascade="all, delete-orphan")
    skill_gaps = relationship("SkillGap", back_populates="sector", cascade="all, delete-orphan")


class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(30), unique=True, index=True, nullable=False)   # e.g. "T_IT_01"
    name = Column(String(200), nullable=False)                           # e.g. "Full Stack Developer"
    sector_id = Column(Integer, ForeignKey("sectors.id"), nullable=False)
    nsqf_level = Column(Integer, nullable=True)                          # NSQF 1-10
    duration_months = Column(Integer, nullable=True)

    sector = relationship("Sector", back_populates="trades")
    occupations = relationship("OccupationMapping", back_populates="trade", cascade="all, delete-orphan")
    demand_records = relationship("LabourDemand", back_populates="trade", cascade="all, delete-orphan")
    supply_records = relationship("TrainingSupply", back_populates="trade", cascade="all, delete-orphan")
    forecasts = relationship("Forecast", back_populates="trade", cascade="all, delete-orphan")
    skill_gaps = relationship("SkillGap", back_populates="trade", cascade="all, delete-orphan")


class Occupation(Base):
    __tablename__ = "occupations"

    id = Column(Integer, primary_key=True, index=True)
    nco_2015_code = Column(String(20), unique=True, index=True, nullable=False)  # e.g. "2512.0101"
    name = Column(String(250), nullable=False)
    description = Column(Text, nullable=True)

    mappings = relationship("OccupationMapping", back_populates="occupation", cascade="all, delete-orphan")


class OccupationMapping(Base):
    __tablename__ = "occupation_mappings"

    id = Column(Integer, primary_key=True, index=True)
    trade_id = Column(Integer, ForeignKey("trades.id"), nullable=False)
    occupation_id = Column(Integer, ForeignKey("occupations.id"), nullable=False)
    alignment_confidence = Column(Float, default=1.0)    # 0.0 - 1.0
    mapping_source = Column(String(200), nullable=True)  # e.g. "NSDC QP-NOS 2023"

    trade = relationship("Trade", back_populates="occupations")
    occupation = relationship("Occupation", back_populates="mappings")
