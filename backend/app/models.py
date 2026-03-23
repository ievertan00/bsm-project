from sqlalchemy import Column, Integer, String, Boolean, Numeric, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    enterprise_size = Column(String, nullable=True)
    establishment_date = Column(Date, nullable=True)
    enterprise_type = Column(String, nullable=True)
    industry_main = Column(String, nullable=True)
    industry_major = Column(String, nullable=True)
    is_high_tech = Column(Boolean, default=False)
    
    business_data = relationship("BusinessData", back_populates="company")

class BusinessData(Base):
    __tablename__ = "business_data"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    loan_amount = Column(Numeric(18, 4), nullable=True)
    guarantee_amount = Column(Numeric(18, 4), nullable=True)
    loan_start_date = Column(Date, nullable=True)
    loan_due_date = Column(Date, nullable=True)
    loan_interest_rate = Column(Numeric(7, 4), nullable=True)
    guarantee_fee_rate = Column(Numeric(7, 4), nullable=True)
    outstanding_loan_balance = Column(Numeric(18, 4), nullable=True)
    outstanding_guarantee_balance = Column(Numeric(18, 4), nullable=True)
    loan_status = Column(String(50), nullable=True)
    cooperative_bank = Column(String(100), nullable=True)
    snapshot_year = Column(Integer, nullable=False)
    snapshot_month = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    company = relationship("Company", back_populates="business_data")
