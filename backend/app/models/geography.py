from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class State(Base):
    __tablename__ = "states"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(10), unique=True, index=True, nullable=False)   # e.g. "OD", "KA"
    name = Column(String(100), unique=True, nullable=False)              # e.g. "Odisha"
    region = Column(String(50), nullable=True)                           # "East", "South"
    is_pilot = Column(Boolean, default=False)                            # True for Odisha

    districts = relationship("District", back_populates="state", cascade="all, delete-orphan")


class District(Base):
    __tablename__ = "districts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    state_id = Column(Integer, ForeignKey("states.id"), nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    economic_tier = Column(String(30), nullable=True)       # "Tier-1", "Tier-2", "Tier-3"
    population_lakhs = Column(Float, nullable=True)

    state = relationship("State", back_populates="districts")
    demand_records = relationship("LabourDemand", back_populates="district", cascade="all, delete-orphan")
    supply_records = relationship("TrainingSupply", back_populates="district", cascade="all, delete-orphan")
    forecasts = relationship("Forecast", back_populates="district", cascade="all, delete-orphan")
    skill_gaps = relationship("SkillGap", back_populates="district", cascade="all, delete-orphan")
