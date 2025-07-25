from flask_sqlalchemy import SQLAlchemy
import datetime

db = SQLAlchemy()

class BusinessData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(255), nullable=False)
    loan_amount = db.Column(db.Numeric(18, 4), nullable=False)
    guarantee_amount = db.Column(db.Numeric(18, 4))
    loan_start_date = db.Column(db.Date, nullable=False)
    loan_due_date = db.Column(db.Date, nullable=False)
    loan_interest_rate = db.Column(db.Numeric(7, 4), nullable=False)
    guarantee_fee_rate = db.Column(db.Numeric(7, 4))
    outstanding_loan_balance = db.Column(db.Numeric(18, 4), nullable=False)
    outstanding_guarantee_balance = db.Column(db.Numeric(18, 4))
    loan_status = db.Column(db.String(50), nullable=False)
    settlement_date = db.Column(db.Date)
    enterprise_classification = db.Column(db.String(50))
    cooperative_bank = db.Column(db.String(100), nullable=False)
    snapshot_year = db.Column(db.Integer, nullable=False)
    snapshot_month = db.Column(db.Integer, nullable=False)
    business_year = db.Column(db.Integer, nullable=True)
    business_type = db.Column(db.String(100))
    enterprise_size = db.Column(db.String(50))
    establishment_date = db.Column(db.Date)
    enterprise_institution_type = db.Column(db.String(100))
    national_standard_industry_category_main = db.Column(db.String(100))
    national_standard_industry_category_major = db.Column(db.String(100))
    qichacha_industry_category_main = db.Column(db.String(100))
    qichacha_industry_category_major = db.Column(db.String(100))
    is_little_giant_enterprise = db.Column(db.Boolean)
    is_srun_sme = db.Column(db.Boolean)
    is_high_tech_enterprise = db.Column(db.Boolean)
    is_innovative_sme = db.Column(db.Boolean)
    is_tech_based_sme = db.Column(db.Boolean)
    is_technology_enterprise = db.Column(db.Boolean)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

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
            'loan_status': self.loan_status,
            'settlement_date': self.settlement_date.strftime('%Y-%m-%d') if self.settlement_date else None,
            'enterprise_classification': self.enterprise_classification,
            'cooperative_bank': self.cooperative_bank,
            'snapshot_year': self.snapshot_year,
            'snapshot_month': self.snapshot_month,
            'business_year': self.business_year,
            'business_type': self.business_type,
            'enterprise_size': self.enterprise_size,
            'establishment_date': self.establishment_date.strftime('%Y-%m-%d') if self.establishment_date else None,
            'enterprise_institution_type': self.enterprise_institution_type,
            'national_standard_industry_category_main': self.national_standard_industry_category_main,
            'national_standard_industry_category_major': self.national_standard_industry_category_major,
            'qichacha_industry_category_main': self.qichacha_industry_category_main,
            'qichacha_industry_category_major': self.qichacha_industry_category_major,
            'is_little_giant_enterprise': self.is_little_giant_enterprise,
            'is_srun_sme': self.is_srun_sme,
            'is_high_tech_enterprise': self.is_high_tech_enterprise,
            'is_innovative_sme': self.is_innovative_sme,
            'is_tech_based_sme': self.is_tech_based_sme,
            'is_technology_enterprise': self.is_technology_enterprise,
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