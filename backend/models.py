from flask_sqlalchemy import SQLAlchemy
import datetime

db = SQLAlchemy()

class BusinessData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(255), nullable=False)
    loan_amount = db.Column(db.Numeric(18, 4), nullable=True)
    guarantee_amount = db.Column(db.Numeric(18, 4))
    loan_start_date = db.Column(db.Date, nullable=True)
    loan_due_date = db.Column(db.Date, nullable=True)
    loan_interest_rate = db.Column(db.Numeric(7, 4), nullable=True)
    guarantee_fee_rate = db.Column(db.Numeric(7, 4), nullable=True)
    outstanding_loan_balance = db.Column(db.Numeric(18, 4), nullable=True)
    outstanding_guarantee_balance = db.Column(db.Numeric(18, 4), nullable=True)
    loan_status = db.Column(db.String(50), nullable=True)
    settlement_date = db.Column(db.Date, nullable=True)
    enterprise_classification = db.Column(db.String(50), nullable=True)
    cooperative_bank = db.Column(db.String(100), nullable=True)
    snapshot_year = db.Column(db.Integer, nullable=False)
    snapshot_month = db.Column(db.Integer, nullable=False)
    business_year = db.Column(db.Integer, nullable=True)
    business_type = db.Column(db.String(100), nullable=True)
    enterprise_size = db.Column(db.String(50), nullable=True)
    establishment_date = db.Column(db.Date, nullable=True)
    enterprise_institution_type = db.Column(db.String(100), nullable=True)
    national_standard_industry_category_main = db.Column(db.String(100),nullable=True)
    national_standard_industry_category_major = db.Column(db.String(100),nullable=True)
    qichacha_industry_category_main = db.Column(db.String(100),nullable=True)
    qichacha_industry_category_major = db.Column(db.String(100),nullable=True)
    is_little_giant_enterprise = db.Column(db.Boolean, nullable=True)
    is_srun_sme = db.Column(db.Boolean, nullable=True)
    is_high_tech_enterprise = db.Column(db.Boolean, nullable=True)
    is_innovative_sme = db.Column(db.Boolean, nullable=True)
    is_tech_based_sme = db.Column(db.Boolean, nullable=True)
    is_technology_enterprise = db.Column(db.Boolean, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'company_name': self.company_name,
            'loan_amount': float(self.loan_amount) if self.loan_amount is not None else None,
            'guarantee_amount': float(self.guarantee_amount) if self.guarantee_amount is not None else None,
            'loan_start_date': self.loan_start_date.strftime('%Y-%m-%d') if self.loan_start_date else None,
            'loan_due_date': self.loan_due_date.strftime('%Y-%m-%d') if self.loan_due_date else None,
            'loan_interest_rate': float(self.loan_interest_rate) if self.loan_interest_rate is not None else None,
            'guarantee_fee_rate': float(self.guarantee_fee_rate) if self.guarantee_fee_rate is not None else None,
            'outstanding_loan_balance': float(self.outstanding_loan_balance) if self.outstanding_loan_balance is not None else None,
            'outstanding_guarantee_balance': float(self.outstanding_guarantee_balance) if self.outstanding_guarantee_balance is not None else None,
            'loan_status': self.loan_status if self.loan_status is not None else None,
            'settlement_date': self.settlement_date.strftime('%Y-%m-%d') if self.settlement_date else None,
            'enterprise_classification': self.enterprise_classification if self.enterprise_classification is not None else None,
            'cooperative_bank': self.cooperative_bank if self.cooperative_bank is not None else None,
            'snapshot_year': self.snapshot_year,
            'snapshot_month': self.snapshot_month,
            'business_year': self.business_year if self.business_year is not None else None,
            'business_type': self.business_type if self.business_type is not None else None,
            'enterprise_size': self.enterprise_size if self.enterprise_size is not None else None,
            'establishment_date': self.establishment_date.strftime('%Y-%m-%d') if self.establishment_date else None,
            'enterprise_institution_type': self.enterprise_institution_type if self.enterprise_institution_type is not None else None,
            'national_standard_industry_category_main': self.national_standard_industry_category_main if self.national_standard_industry_category_main is not None else None,
            'national_standard_industry_category_major': self.national_standard_industry_category_major if self.national_standard_industry_category_major is not None else None,
            'qichacha_industry_category_main': self.qichacha_industry_category_main if self.qichacha_industry_category_main is not None else None,
            'qichacha_industry_category_major': self.qichacha_industry_category_major if self.qichacha_industry_category_major is not None else None,
            'is_little_giant_enterprise': self.is_little_giant_enterprise if self.is_little_giant_enterprise is not None else None,
            'is_srun_sme': self.is_srun_sme if self.is_srun_sme is not None else None,
            'is_high_tech_enterprise': self.is_high_tech_enterprise if self.is_high_tech_enterprise is not None else None,
            'is_innovative_sme': self.is_innovative_sme if self.is_innovative_sme is not None else None,
            'is_tech_based_sme': self.is_tech_based_sme if self.is_tech_based_sme is not None else None,
            'is_technology_enterprise': self.is_technology_enterprise if self.is_technology_enterprise is not None else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class DataHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_id = db.Column(db.Integer, db.ForeignKey('business_data.id'), nullable=False)
    changed_by = db.Column(db.String(100))
    changed_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    field_name = db.Column(db.String(50))
    old_value = db.Column(db.String(255))
    new_value = db.Column(db.String(255))

    def to_dict(self):
        return {
            'id': self.id,
            'data_id': self.data_id,
            'changed_by': self.changed_by,
            'changed_at': self.changed_at.isoformat() if self.changed_at else None,
            'field_name': self.field_name,
            'old_value': self.old_value,
            'new_value': self.new_value
        }

# class MonthlyData(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     year_month = db.Column(db.String(7), unique=True, nullable=False)
#     total_loan_amount = db.Column(db.Float, nullable=False)
#     total_guarantee_amount = db.Column(db.Float, nullable=False)
#     total_loan_balance = db.Column(db.Float, nullable=False)
#     total_guarantee_balance = db.Column(db.Float, nullable=False)
#     record_count = db.Column(db.Integer, nullable=False)
#     created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
#
#     def to_dict(self):
#         return {
#             'id': self.id,
#             'year_month': self.year_month,
#             'total_loan_amount': self.total_loan_amount,
#             'total_guarantee_amount': self.total_guarantee_amount,
#             'total_loan_balance': self.total_loan_balance,
#             'total_guarantee_balance': self.total_guarantee_balance,
#             'record_count': self.record_count,
#             'created_at': self.created_at.isoformat() if self.created_at else None
#         }