import pandas as pd
from sqlalchemy.orm import Session
from . import models, schemas
import datetime

def import_excel_data(file_path: str, db: Session):
    # Read the Excel file
    df = pd.read_excel(file_path)
    
    # Required columns for Company
    # enterprise_name, enterprise_size, establishment_date, enterprise_type, industry_main, industry_major, is_high_tech
    
    # Required columns for BusinessData
    # loan_amount, guarantee_amount, loan_start_date, loan_due_date, loan_interest_rate, guarantee_fee_rate, outstanding_loan_balance, outstanding_guarantee_balance, loan_status, cooperative_bank, snapshot_year, snapshot_month
    
    imported_count = 0
    
    for _, row in df.iterrows():
        company_name = str(row.get('enterprise_name', '')).strip()
        if not company_name:
            continue
            
        # 1. Get or Create Company
        company = db.query(models.Company).filter(models.Company.name == company_name).first()
        if not company:
            company = models.Company(
                name=company_name,
                enterprise_size=row.get('enterprise_size'),
                establishment_date=pd.to_datetime(row.get('establishment_date')).date() if pd.notnull(row.get('establishment_date')) else None,
                enterprise_type=row.get('enterprise_type'),
                industry_main=row.get('industry_main'),
                industry_major=row.get('industry_major'),
                is_high_tech=bool(row.get('is_high_tech', False))
            )
            db.add(company)
            db.flush() # To get the company.id
            
        # 2. Add Business Data
        business_entry = models.BusinessData(
            company_id=company.id,
            loan_amount=row.get('loan_amount'),
            guarantee_amount=row.get('guarantee_amount'),
            loan_start_date=pd.to_datetime(row.get('loan_start_date')).date() if pd.notnull(row.get('loan_start_date')) else None,
            loan_due_date=pd.to_datetime(row.get('loan_due_date')).date() if pd.notnull(row.get('loan_due_date')) else None,
            loan_interest_rate=row.get('loan_interest_rate'),
            guarantee_fee_rate=row.get('guarantee_fee_rate'),
            outstanding_loan_balance=row.get('outstanding_loan_balance'),
            outstanding_guarantee_balance=row.get('outstanding_guarantee_balance'),
            loan_status=row.get('loan_status'),
            cooperative_bank=row.get('cooperative_bank'),
            snapshot_year=int(row.get('snapshot_year', datetime.datetime.now().year)),
            snapshot_month=int(row.get('snapshot_month', datetime.datetime.now().month))
        )
        db.add(business_entry)
        imported_count += 1
        
    db.commit()
    return imported_count
