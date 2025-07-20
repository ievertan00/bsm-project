import pandas as pd
from models import db, BusinessData, DataHistory
from sqlalchemy import and_
from datetime import datetime

def import_data_from_excel(file, year_month):
    # ... (this function remains unchanged)
    BusinessData.query.filter_by(year_month=year_month).delete()
    db.session.commit()

    df = pd.read_excel(file)
    for _, row in df.iterrows():
        loan_amount = round(float(row.get('借款金额（万元）', 0)), 2)
        guarantee_amount = round(float(row.get('担保金额（万元）', 0)), 2)
        loan_balance = round(float(row.get('借款余额（万元）', 0)), 2)
        guarantee_balance = round(float(row.get('担保余额（万元）', 0)), 2)

        new_data = BusinessData(
            year_month=year_month,
            company_name=row.get('企业名称'),
            loan_amount=loan_amount if loan_amount > 0 else None,
            guarantee_amount=guarantee_amount if guarantee_amount >= 0 else None,
            loan_balance=loan_balance if loan_balance > 0 else None,
            guarantee_balance=guarantee_balance if guarantee_balance >= 0 else None,
            loan_status=row.get('借据状态'),
            loan_start_date=pd.to_datetime(row.get('借款起始日')).date() if pd.notna(row.get('借款起始日')) else None,
            loan_end_date=pd.to_datetime(row.get('借款到期日')).date() if pd.notna(row.get('借款到期日')) else None,
            cooperation_bank=row.get('合作银行'),
            business_type=row.get('业务类型'),
            business_year=int(row.get('业务年度')) if pd.notna(row.get('业务年度')) else None
        )
        db.session.add(new_data)
    db.session.commit()

def get_statistics(year_month):
    # ... (this function remains unchanged)
    base_query = BusinessData.query.filter_by(year_month=year_month)
    df = pd.DataFrame([d.to_dict() for d in base_query.all()])

    if df.empty:
        return {}

    total_loan_amount_month = df['loan_amount'].sum()
    total_guarantee_amount_month = df['guarantee_amount'].sum()

    bank_stats = df.groupby('cooperation_bank').agg(
        total_loan_amount=('loan_amount', 'sum'),
        total_guarantee_amount=('guarantee_amount', 'sum'),
        business_count=('id', 'count'),
        company_count=('company_name', 'nunique')
    ).reset_index()
    bank_stats['loan_percentage'] = (bank_stats['total_loan_amount'] / total_loan_amount_month) * 100
    bank_stats['guarantee_percentage'] = (bank_stats['total_guarantee_amount'] / total_guarantee_amount_month) * 100

    year_stats = df.groupby('business_year').agg(
        total_loan_amount=('loan_amount', 'sum'),
        business_count=('id', 'count'),
        company_count=('company_name', 'nunique')
    ).reset_index()
    all_companies = {c.company_name for c in BusinessData.query.with_entities(BusinessData.company_name).distinct()}
    year_stats['total_companies_all_time'] = len(all_companies)

    type_stats = df.groupby('business_type').agg(
        total_loan_amount=('loan_amount', 'sum'),
        business_count=('id', 'count'),
        company_count=('company_name', 'nunique')
    ).reset_index()
    type_stats['loan_percentage'] = (type_stats['total_loan_amount'] / total_loan_amount_month) * 100

    from datetime import timedelta
    current_month_dt = datetime.strptime(year_month, '%Y-%m')
    prev_month_dt = current_month_dt - timedelta(days=1)
    prev_year_month = prev_month_dt.strftime('%Y-%m')
    
    prev_month_data = BusinessData.query.filter_by(year_month=prev_year_month).all()
    df_prev = pd.DataFrame([d.to_dict() for d in prev_month_data])

    current_companies = set(df['company_name'].unique())
    prev_companies = set(df_prev['company_name'].unique()) if not df_prev.empty else set()
    new_companies = current_companies - prev_companies

    new_loan_amount = df[df['company_name'].isin(new_companies)]['loan_amount'].sum()
    new_guarantee_amount = df[df['company_name'].isin(new_companies)]['guarantee_amount'].sum()
    
    monthly_growth = {
        'new_loan_amount': new_loan_amount,
        'new_guarantee_amount': new_guarantee_amount,
        'new_company_count': len(new_companies),
        'current_month_total_loan': total_loan_amount_month,
        'previous_month_total_loan': df_prev['loan_amount'].sum() if not df_prev.empty else 0,
    }

    return {
        'by_bank': bank_stats.to_dict(orient='records'),
        'by_year': year_stats.to_dict(orient='records'),
        'by_type': type_stats.to_dict(orient='records'),
        'monthly_growth': monthly_growth,
        'loan_status_distribution': df['loan_status'].value_counts().reset_index().to_dict(orient='records')
    }

def update_business_data(data_id, new_data):
    data_entry = BusinessData.query.get(data_id)
    if not data_entry:
        raise Exception("Data not found")

    # Remove immutable fields from the update data
    new_data.pop('id', None)
    new_data.pop('year_month', None)
    new_data.pop('created_at', None)

    for key, value in new_data.items():
        # --- Data Type Coercion and Validation ---
        if key in ['loan_start_date', 'loan_end_date']:
            if value:
                try:
                    value = datetime.strptime(value, '%Y-%m-%d').date()
                except (ValueError, TypeError):
                    value = None
            else:
                value = None
        
        elif key == 'business_year':
            if value == '' or value is None:
                value = None
            else:
                try:
                    value = int(value)
                except (ValueError, TypeError):
                    value = None

        elif key in ['loan_amount', 'guarantee_amount', 'loan_balance', 'guarantee_balance']:
            if value == '' or value is None:
                value = None
            else:
                try:
                    value = float(value)
                except (ValueError, TypeError):
                    value = None

        old_value = getattr(data_entry, key)

        # --- Compare and Log History ---
        if old_value != value:
            history_log = DataHistory(
                data_id=data_id,
                field_name=key,
                old_value=str(old_value) if old_value is not None else None,
                new_value=str(value) if value is not None else None,
                changed_by="user"
            )
            db.session.add(history_log)
            setattr(data_entry, key, value)
    
    db.session.commit()
    return data_entry

def get_data_history(data_id):
    history_records = DataHistory.query.filter_by(data_id=data_id).order_by(DataHistory.changed_at.desc()).all()
    return [h.to_dict() for h in history_records]

def get_version_comparison(year_month1, year_month2):
    # ... (this function remains unchanged)
    data1 = BusinessData.query.filter_by(year_month=year_month1).all()
    df1 = pd.DataFrame([d.to_dict() for d in data1])

    data2 = BusinessData.query.filter_by(year_month=year_month2).all()
    df2 = pd.DataFrame([d.to_dict() for d in data2])

    if df1.empty or df2.empty:
        return {"error": "Data not available for one or both selected periods."}

    summary1 = {
        "total_loan_amount": df1['loan_amount'].sum(),
        "total_guarantee_amount": df1['guarantee_amount'].sum(),
        "total_loan_balance": df1['loan_balance'].sum(),
        "total_guarantee_balance": df1['guarantee_balance'].sum(),
        "business_count": len(df1),
        "company_count": df1['company_name'].nunique()
    }

    summary2 = {
        "total_loan_amount": df2['loan_amount'].sum(),
        "total_guarantee_amount": df2['guarantee_amount'].sum(),
        "total_loan_balance": df2['loan_balance'].sum(),
        "total_guarantee_balance": df2['guarantee_balance'].sum(),
        "business_count": len(df2),
        "company_count": df2['company_name'].nunique()
    }

    def calculate_percentage_change(old, new):
        if old == 0:
            return float('inf') if new > 0 else 0.0
        return ((new - old) / old) * 100

    percentage_changes = {key: calculate_percentage_change(summary1[key], summary2[key]) for key in summary1}

    companies1 = set(df1['company_name'].unique())
    companies2 = set(df2['company_name'].unique())

    new_companies = companies2 - companies1
    lost_companies = companies1 - companies2
    continuing_companies = companies1.intersection(companies2)

    new_companies_loan = df2[df2['company_name'].isin(new_companies)]['loan_amount'].sum()
    lost_companies_loan = df1[df1['company_name'].isin(lost_companies)]['loan_amount'].sum()
    continuing_companies_loan1 = df1[df1['company_name'].isin(continuing_companies)]['loan_amount'].sum()
    continuing_companies_loan2 = df2[df2['company_name'].isin(continuing_companies)]['loan_amount'].sum()

    return {
        "summary1": summary1,
        "summary2": summary2,
        "changes": {
            "total_loan_amount_change": summary2['total_loan_amount'] - summary1['total_loan_amount'],
            "company_count_change": summary2['company_count'] - summary1['company_count']
        },
        "percentage_changes": percentage_changes,
        "company_analysis": {
            "new_companies": list(new_companies),
            "lost_companies": list(lost_companies),
            "continuing_companies": list(continuing_companies),
            "new_companies_count": len(new_companies),
            "lost_companies_count": len(lost_companies),
            "continuing_companies_count": len(continuing_companies),
            "new_companies_loan": new_companies_loan,
            "lost_companies_loan": lost_companies_loan,
            "continuing_companies_loan_change": continuing_companies_loan2 - continuing_companies_loan1
        }
    }