from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import get_db
from ..models import BusinessData, Company
from .auth import get_current_user
from typing import List, Dict

router = APIRouter()

@router.get("/summary")
async def get_summary(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    total_companies = db.query(func.count(Company.id)).scalar()
    
    business_summary = db.query(
        func.sum(BusinessData.loan_amount).label("total_loan"),
        func.sum(BusinessData.guarantee_amount).label("total_guarantee"),
        func.sum(BusinessData.outstanding_loan_balance).label("total_outstanding_loan"),
        func.sum(BusinessData.outstanding_guarantee_balance).label("total_outstanding_guarantee")
    ).first()

    return {
        "total_companies": total_companies or 0,
        "total_loan": float(business_summary.total_loan or 0),
        "total_guarantee": float(business_summary.total_guarantee or 0),
        "total_outstanding_loan": float(business_summary.total_outstanding_loan or 0),
        "total_outstanding_guarantee": float(business_summary.total_outstanding_guarantee or 0)
    }

@router.get("/growth")
async def get_growth(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    growth_data = db.query(
        BusinessData.snapshot_year,
        BusinessData.snapshot_month,
        func.sum(BusinessData.loan_amount).label("total_loan"),
        func.sum(BusinessData.guarantee_amount).label("total_guarantee"),
        func.sum(BusinessData.outstanding_loan_balance).label("total_outstanding_loan"),
        func.sum(BusinessData.outstanding_guarantee_balance).label("total_outstanding_guarantee")
    ).group_by(
        BusinessData.snapshot_year,
        BusinessData.snapshot_month
    ).order_by(
        BusinessData.snapshot_year.asc(),
        BusinessData.snapshot_month.asc()
    ).all()

    result = []
    for row in growth_data:
        result.append({
            "period": f"{row.snapshot_year}-{row.snapshot_month:02d}",
            "total_loan": float(row.total_loan or 0),
            "total_guarantee": float(row.total_guarantee or 0),
            "total_outstanding_loan": float(row.total_outstanding_loan or 0),
            "total_outstanding_guarantee": float(row.total_outstanding_guarantee or 0)
        })

    return result
