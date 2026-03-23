from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal

# User schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# BusinessData schemas
class BusinessDataBase(BaseModel):
    loan_amount: Optional[Decimal] = None
    guarantee_amount: Optional[Decimal] = None
    loan_start_date: Optional[date] = None
    loan_due_date: Optional[date] = None
    loan_interest_rate: Optional[Decimal] = None
    guarantee_fee_rate: Optional[Decimal] = None
    outstanding_loan_balance: Optional[Decimal] = None
    outstanding_guarantee_balance: Optional[Decimal] = None
    loan_status: Optional[str] = None
    cooperative_bank: Optional[str] = None
    snapshot_year: int
    snapshot_month: int

class BusinessDataCreate(BusinessDataBase):
    company_id: int

class BusinessData(BusinessDataBase):
    id: int
    company_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Company schemas
class CompanyBase(BaseModel):
    name: str
    enterprise_size: Optional[str] = None
    establishment_date: Optional[date] = None
    enterprise_type: Optional[str] = None
    industry_main: Optional[str] = None
    industry_major: Optional[str] = None
    is_high_tech: bool = False

class CompanyCreate(CompanyBase):
    pass

class Company(CompanyBase):
    id: int
    business_data: List[BusinessData] = []

    class Config:
        from_attributes = True
