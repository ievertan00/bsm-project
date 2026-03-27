from pydantic import BaseModel, ConfigDict
from datetime import date, datetime
from typing import Optional
from decimal import Decimal

# Company schemas
class CompanyBase(BaseModel):
    company_name: str
    enterprise_size: Optional[str] = None
    establishment_date: Optional[date] = None
    enterprise_institution_type: Optional[str] = None
    national_standard_industry_category_main: Optional[str] = None
    national_standard_industry_category_major: Optional[str] = None
    qichacha_industry_category_main: Optional[str] = None
    qichacha_industry_category_major: Optional[str] = None
    is_little_giant_enterprise: Optional[bool] = None
    is_srun_sme: Optional[bool] = None
    is_high_tech_enterprise: Optional[bool] = None
    is_innovative_sme: Optional[bool] = None
    is_tech_based_sme: Optional[bool] = None
    is_technology_enterprise: Optional[bool] = None
    qyjh_category: Optional[str] = None

class CompanyCreate(CompanyBase):
    pass

class Company(CompanyBase):
    id: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

# BusinessData schemas
class BusinessDataBase(BaseModel):
    company_id: int
    loan_amount: Optional[Decimal] = None
    guarantee_amount: Optional[Decimal] = None
    loan_start_date: Optional[date] = None
    loan_due_date: Optional[date] = None
    loan_interest_rate: Optional[Decimal] = None
    guarantee_fee_rate: Optional[Decimal] = None
    outstanding_loan_balance: Optional[Decimal] = None
    outstanding_guarantee_balance: Optional[Decimal] = None
    loan_status: Optional[str] = None
    settlement_date: Optional[date] = None
    enterprise_classification: Optional[str] = None
    cooperative_bank: Optional[str] = None
    snapshot_year: int
    snapshot_month: int
    business_year: Optional[int] = None
    business_type: Optional[str] = None

class BusinessDataCreate(BusinessDataBase):
    pass

class BusinessData(BusinessDataBase):
    id: int
    created_at: Optional[datetime] = None
    company: Optional[Company] = None

    model_config = ConfigDict(from_attributes=True)

# QCCIndustry schemas
class QCCIndustryBase(BaseModel):
    company_name: str
    enterprise_scale: Optional[str] = None
    enterprise_type: Optional[str] = None
    national_standard_industry_category_main: Optional[str] = None
    national_standard_industry_category_major: Optional[str] = None
    qcc_industry_category_main: Optional[str] = None
    qcc_industry_category_major: Optional[str] = None

class QCCIndustryCreate(QCCIndustryBase):
    pass

class QCCIndustry(QCCIndustryBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# QCCTech schemas
class QCCTechBase(BaseModel):
    company_name: str
    is_little_giant_enterprise: Optional[bool] = None
    is_srun_sme: Optional[bool] = None
    is_high_tech_enterprise: Optional[bool] = None
    is_innovative_sme: Optional[bool] = None
    is_tech_based_sme: Optional[bool] = None

class QCCTechCreate(QCCTechBase):
    pass

class QCCTech(QCCTechBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
