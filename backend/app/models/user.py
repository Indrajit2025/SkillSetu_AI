import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from app.database import Base

class UserRole(str, enum.Enum):
    POLICY_MAKER = "policy_maker"
    ANALYST = "analyst"
    TRAINING_INSTITUTE = "training_institute"
    ADMIN = "admin"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(150), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.ANALYST, nullable=False)
    organization = Column(String(200), nullable=True)  # e.g., "Skill Development and Technical Education Dept"
    department = Column(String(150), nullable=True)    # e.g., "Labour Market Analytics Wing"
    designation = Column(String(150), nullable=True)   # e.g., "Chief Planning Officer"
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
