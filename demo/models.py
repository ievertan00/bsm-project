import datetime
from sqlalchemy import Column, Integer, String, Numeric, Date, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(255), nullable=False, unique=True, index=True)
    enterprise_size = Column(String(50), nullable=True)
    establishment_date = Column(Date, nullable=True)
    enterprise_institution_type = Column(String(100), nullable=True)
    national_standard_industry_category_main = Column(String(100), nullable=True)
    national_standard_industry_category_major = Column(String(100), nullable=True)
    qichacha_industry_category_main = Column(String(100), nullable=True)
    qichacha_industry_category_major = Column(String(100), nullable=True)
    is_little_giant_enterprise = Column(Boolean, nullable=True)
    is_srun_sme = Column(Boolean, nullable=True)
    is_high_tech_enterprise = Column(Boolean, nullable=True)
    is_innovative_sme = Column(Boolean, nullable=True)
    is_tech_based_sme = Column(Boolean, nullable=True)
    is_technology_enterprise = Column(Boolean, nullable=True)
    qyjh_category = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=True)

    business_records = relationship("BusinessData", back_populates="company")

class BusinessData(Base):
    __tablename__ = "business_data"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    loan_amount = Column(Numeric(18, 6), nullable=True)
    guarantee_amount = Column(Numeric(18, 6), nullable=True)
    loan_start_date = Column(Date, nullable=True)
    loan_due_date = Column(Date, nullable=True)
    loan_interest_rate = Column(Numeric(10, 6), nullable=True)
    guarantee_fee_rate = Column(Numeric(10, 6), nullable=True)
    outstanding_loan_balance = Column(Numeric(18, 6), nullable=True)
    outstanding_guarantee_balance = Column(Numeric(18, 6), nullable=True)
    loan_status = Column(String(50), nullable=True)
    settlement_date = Column(Date, nullable=True)
    enterprise_classification = Column(String(50), nullable=True)
    cooperative_bank = Column(String(100), nullable=True)
    snapshot_year = Column(Integer, nullable=False)
    snapshot_month = Column(Integer, nullable=False)
    business_year = Column(Integer, nullable=True)
    business_type = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=True)

    company = relationship("Company", back_populates="business_records")

class QCCIndustry(Base):
    __tablename__ = "qcc_industry"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(255), nullable=False, index=True)
    enterprise_scale = Column(String(50), nullable=True)
    enterprise_type = Column(String(100), nullable=True)
    national_standard_industry_category_main = Column(String(100), nullable=True)
    national_standard_industry_category_major = Column(String(100), nullable=True)
    qcc_industry_category_main = Column(String(100), nullable=True)
    qcc_industry_category_major = Column(String(100), nullable=True)

class QCCTech(Base):
    __tablename__ = "qcc_tech"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(255), nullable=False, index=True)
    is_little_giant_enterprise = Column(Boolean, nullable=True)
    is_srun_sme = Column(Boolean, nullable=True)
    is_high_tech_enterprise = Column(Boolean, nullable=True)
    is_innovative_sme = Column(Boolean, nullable=True)
    is_tech_based_sme = Column(Boolean, nullable=True)

class QYJHList(Base):
    __tablename__ = "qyjh_list"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(255), nullable=False, index=True)
    qyjh_category = Column(String(100), nullable=True)
