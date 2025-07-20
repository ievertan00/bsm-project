from flask_sqlalchemy import SQLAlchemy
import datetime

db = SQLAlchemy()

class BusinessData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    year_month = db.Column(db.String(7), nullable=False)  # Format: YYYY-MM
    company_name = db.Column(db.String(100))
    loan_amount = db.Column(db.Float)
    guarantee_amount = db.Column(db.Float)
    loan_balance = db.Column(db.Float)
    guarantee_balance = db.Column(db.Float)
    loan_status = db.Column(db.String(20))
    loan_start_date = db.Column(db.Date)
    loan_end_date = db.Column(db.Date)
    cooperation_bank = db.Column(db.String(100))
    business_type = db.Column(db.String(50))
    business_year = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'year_month': self.year_month,
            'company_name': self.company_name,
            'loan_amount': self.loan_amount,
            'guarantee_amount': self.guarantee_amount,
            'loan_balance': self.loan_balance,
            'guarantee_balance': self.guarantee_balance,
            'loan_status': self.loan_status,
            'loan_start_date': self.loan_start_date.strftime('%Y-%m-%d') if self.loan_start_date else None,
            'loan_end_date': self.loan_end_date.strftime('%Y-%m-%d') if self.loan_end_date else None,
            'cooperation_bank': self.cooperation_bank,
            'business_type': self.business_type,
            'business_year': self.business_year,
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