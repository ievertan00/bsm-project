import pandas as pd
from models import db, BusinessData, DataHistory
from sqlalchemy import func
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def import_data_from_excel(file, year, month):
    df = pd.read_excel(file)
    
    # Delete existing data for the specified year and month
    db.session.query(BusinessData).filter_by(snapshot_year=year, snapshot_month=month).delete()
    db.session.commit() # Commit the deletion before adding new data

    for _, row in df.iterrows():
        company_name = row.get('企业名称')
        loan_start_date = pd.to_datetime(row.get('借款起始日')).date() if pd.notna(row.get('借款起始日')) else None
        loan_due_date = pd.to_datetime(row.get('借款到期日')).date() if pd.notna(row.get('借款到期日')) else None
        # business_year_from_excel = int(row.get('业务年度')) if pd.notna(row.get('业务年度')) else None # This line is removed as per new logic

        loan_interest_rate_val = row.get('借款利率')
        logger.debug(f"Original '借款利率': {loan_interest_rate_val} (Type: {type(loan_interest_rate_val)})")
        if pd.notna(loan_interest_rate_val) and str(loan_interest_rate_val).strip() != '':
            try:
                loan_interest_rate_val = float(loan_interest_rate_val)
            except (ValueError, TypeError):
                loan_interest_rate_val = 0 # Default to 0 if conversion fails
        else:
            loan_interest_rate_val = 0
        logger.debug(f"Processed '借款利率': {loan_interest_rate_val}")

        guarantee_fee_rate_val = row.get('担保费率')
        logger.debug(f"Original '担保费率': {guarantee_fee_rate_val} (Type: {type(guarantee_fee_rate_val)})")
        if pd.notna(guarantee_fee_rate_val) and str(guarantee_fee_rate_val).strip() != '':
            try:
                guarantee_fee_rate_val = float(guarantee_fee_rate_val)
            except (ValueError, TypeError):
                guarantee_fee_rate_val = 0 # Default to 0 if conversion fails
        else:
            guarantee_fee_rate_val = 0
        logger.debug(f"Processed '担保费率': {guarantee_fee_rate_val}")

        new_data = BusinessData(
            company_name=company_name,
            loan_amount=row.get('借款金额（万元）'),
            guarantee_amount=row.get('担保金额（万元）'),
            loan_start_date=loan_start_date,
            loan_due_date=loan_due_date,
            loan_interest_rate=loan_interest_rate_val,
            guarantee_fee_rate=guarantee_fee_rate_val,
            outstanding_loan_balance=row.get('借款余额（万元）'),
            outstanding_guarantee_balance=row.get('担保余额（万元）'),
            loan_status=row.get('借据状态'),
            settlement_date=pd.to_datetime(row.get('结清日期')).date() if pd.notna(row.get('结清日期')) else None,
            enterprise_classification=row.get('企业划型'),
            cooperative_bank=row.get('合作银行'),
            snapshot_year=year,
            snapshot_month=month,
            business_year=int(row.get('业务年度')) if pd.notna(row.get('业务年度')) else None,
            business_type=row.get('业务类型'),
            enterprise_size=row.get('企业规模'),
            establishment_date=pd.to_datetime(row.get('成立日期')).date() if pd.notna(row.get('成立日期')) else None,
            registered_capital=row.get('注册资本'),
            enterprise_institution_type=row.get('企业（机构）类型'),
            national_standard_industry_category_main=row.get('国标行业门类'),
            national_standard_industry_category_major=row.get('国标行业大类'),
            qichacha_industry_category_main=row.get('企查查行业门类'),
            qichacha_industry_category_major=row.get('企查查行业大类'),
            is_little_giant_enterprise=bool(row.get('专精特新“小巨人”企业')) if pd.notna(row.get('专精特新“小巨人”企业')) else None,
            is_srun_sme=bool(row.get('专精特新中小企业')) if pd.notna(row.get('专精特新中小企业')) else None,
            is_high_tech_enterprise=bool(row.get('高新技术企业')) if pd.notna(row.get('高新技术企业')) else None,
            is_innovative_sme=bool(row.get('创新型中小企业')) if pd.notna(row.get('创新型中小企业')) else None,
            is_tech_based_sme=bool(row.get('科技型中小企业')) if pd.notna(row.get('科技型中小企业')) else None,
            is_technology_enterprise=bool(row.get('科技企业')) if pd.notna(row.get('科技企业')) else None
        )
        db.session.add(new_data)
    db.session.commit()

def get_statistics(year=None, month=None):
    if not year or not month:
        return {
            "cumulative_loan_amount": 0,
            "cumulative_guarantee_amount": 0,
            "cumulative_company_count": 0,
            "new_companies_this_year_count": 0,
            "new_companies_this_year_loan": 0,
            "in_force_companies_count": 0,
            "total_loan_balance": 0,
            "total_guarantee_balance": 0,
        }

    # 1. Fetch the data for the selected snapshot (current period)
    current_snapshot_query = BusinessData.query.filter_by(snapshot_year=year, snapshot_month=month)
    current_snapshot_data = current_snapshot_query.all()
    df_current = pd.DataFrame([d.to_dict() for d in current_snapshot_data])

    if df_current.empty:
        return {
            "cumulative_loan_amount": 0,
            "cumulative_guarantee_amount": 0,
            "cumulative_company_count": 0,
            "new_companies_this_year_count": 0,
            "new_companies_this_year_loan": 0,
            "in_force_companies_count": 0,
            "total_loan_balance": 0,
            "total_guarantee_balance": 0,
        }

    # 1. 累计借款金额
    cumulative_loan_amount = df_current['loan_amount'].sum()
    # 2. 累计担保金额
    cumulative_guarantee_amount = df_current['guarantee_amount'].sum()
    # 3. 累计借款企业数量
    cumulative_company_count = df_current['company_name'].nunique()
    # 4. 本年新增企业数量
    new_companies_this_year_count = df_current[df_current['business_year']==year]['company_name'].nunique()
    # 5. 本年新增借款金额
    new_companies_this_year_loan = df_current[df_current['business_year']==year]['loan_amount'].sum()
    # 6. 本年新增担保金额
    new_companies_this_year_gurantee = df_current[df_current['business_year']==year]['guarantee_amount'].sum()
    # 7. 在保企业数量
    in_force_companies_count = df_current[(df_current['loan_status'] == '正常') & (df_current['outstanding_loan_balance'] > 0)]['company_name'].nunique()
    # 8. 借款余额
    total_loan_balance = df_current['outstanding_loan_balance'].sum()
    # 9. 担保余额
    total_guarantee_balance = df_current['outstanding_guarantee_balance'].sum()

    result = {
        'cumulative_loan_amount': float(cumulative_loan_amount),
        'cumulative_guarantee_amount': float(cumulative_guarantee_amount),
        'cumulative_company_count': int(cumulative_company_count),
        'new_companies_this_year_count': int(new_companies_this_year_count),
        'new_companies_this_year_loan': float(new_companies_this_year_loan),
        'new_companies_this_year_guarantee': float(new_companies_this_year_gurantee),
        'in_force_companies_count': int(in_force_companies_count),
        'total_loan_balance': float(total_loan_balance),
        'total_guarantee_balance': float(total_guarantee_balance),
    }
    return result

def update_business_data(data_id, new_data):
    data_entry = BusinessData.query.get(data_id)
    if not data_entry:
        raise Exception("Data not found")

    # Remove immutable fields
    new_data.pop('id', None)
    new_data.pop('created_at', None)

    for key, value in new_data.items():
        # Type Coercion and Validation
        if key in ['loan_start_date', 'loan_due_date', 'settlement_date', 'establishment_date']:
            value = datetime.strptime(value, '%Y-%m-%d').date() if value else None
        elif key in ['loan_amount', 'guarantee_amount', 'outstanding_loan_balance', 'outstanding_guarantee_balance', 'loan_interest_rate', 'guarantee_fee_rate', 'registered_capital']:
            value = float(value) if value is not None else None
        elif key.startswith('is_'):
            value = bool(value) if value is not None else None
        
        old_value = getattr(data_entry, key)

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
    year1, month1 = map(int, year_month1.split('-'))
    year2, month2 = map(int, year_month2.split('-'))

    data1 = BusinessData.query.filter_by(snapshot_year=year1, snapshot_month=month1).all()
    df1 = pd.DataFrame([d.to_dict() for d in data1])

    data2 = BusinessData.query.filter_by(snapshot_year=year2, snapshot_month=month2).all()
    df2 = pd.DataFrame([d.to_dict() for d in data2])

    # Helper functions to safely get sum and unique count
    def get_safe_sum(df, column):
        if not df.empty and column in df.columns:
            return df[column].sum() if not pd.isna(df[column].sum()) else 0.0
        return 0.0

    def get_safe_unique_count(df, column):
        if not df.empty and column in df.columns:
            return df[column].nunique()
        return 0

    def get_this_year_sum(df, column, year):
        if not df.empty and column in df.columns:
            return df[df['business_year'==year]][column].sum()
        return 0.0

    def get_this_year_count(df, column, year):
        if not df.empty and column in df.columns:
            return df[df['business_year'==year]][column].nunique()
        return 0

    if df1.empty and df2.empty:
        return {"error": "Data not available for both selected periods."}
    
    # If one is empty, provide a more specific error or handle gracefully
    if df1.empty:
        return {"error": f"Data not available for {year_month1}."}
    if df2.empty:
        return {"error": f"Data not available for {year_month2}."}


    summary1 = {
        "total_loan_amount": get_safe_sum(df1, 'loan_amount'),
        "total_guarantee_amount": get_safe_sum(df1, 'guarantee_amount'),
        "new_companies_this_year_loan": get_this_year_sum(df1, 'new_companies_this_year_loan',year1),
        "new_companies_this_year_guarantee": get_this_year_sum(df1, 'new_companies_this_year_guarantee',year1),
        "total_loan_balance": get_safe_sum(df1, 'outstanding_loan_balance'),
        "total_guarantee_balance": get_safe_sum(df1, 'outstanding_guarantee_balance'),
        "business_count": len(df1), # len(df) is safe even if df is empty
        "company_count": get_safe_unique_count(df1, 'company_name'),
        "new_companies_this_year_count": get_this_year_count(df1, 'new_companies_this_year',year1),
    }

    summary2 = {
        "total_loan_amount": get_safe_sum(df2, 'loan_amount'),
        "total_guarantee_amount": get_safe_sum(df2, 'guarantee_amount'),
        "new_companies_this_year_loan": get_this_year_sum(df2, 'new_companies_this_year_loan',year2),
        "new_companies_this_year_guarantee": get_this_year_sum(df2, 'new_companies_this_year_guarantee',year2),
        "total_loan_balance": get_safe_sum(df2, 'outstanding_loan_balance'),
        "total_guarantee_balance": get_safe_sum(df2, 'outstanding_guarantee_balance'),
        "business_count": len(df2), # len(df) is safe even if df is empty
        "company_count": get_safe_unique_count(df2, 'company_name'),
        "new_companies_this_year_count": get_this_year_count(df2, 'new_companies_this_year',year2),
    }

    def calculate_percentage_change(old, new):
        if old == 0:
            return float('inf') if new > 0 else 0.0
        return ((new - old) / old) * 100

    percentage_changes = {key: calculate_percentage_change(summary1[key], summary2[key]) for key in summary1}

    companies1 = set(df1['company_name'].unique()) if 'company_name' in df1.columns and not df1.empty else set()
    companies2 = set(df2['company_name'].unique()) if 'company_name' in df2.columns and not df2.empty else set()

    new_companies = list(companies2 - companies1)
    lost_companies = list(companies1 - companies2)
    continuing_companies = list(companies1.intersection(companies2))

    new_companies_loan = get_safe_sum(df2[df2['company_name'].isin(new_companies)], 'loan_amount')
    lost_companies_loan = get_safe_sum(df1[df1['company_name'].isin(lost_companies)], 'loan_amount')
    continuing_companies_loan1 = get_safe_sum(df1[df1['company_name'].isin(continuing_companies)], 'loan_amount')
    continuing_companies_loan2 = get_safe_sum(df2[df2['company_name'].isin(continuing_companies)], 'loan_amount')


    return {
        "summary1": summary1,
        "summary2": summary2,
        "changes": {
            "total_loan_amount_change": summary2['total_loan_amount'] - summary1['total_loan_amount'],
            "total_guarantee_amount_change": summary2['total_guarantee_amount'] - summary1['total_guarantee_amount'],
            "total_loan_balance_change": summary2['total_loan_balance'] - summary1['total_loan_balance'],
            "total_guarantee_balance_change": summary2['total_guarantee_balance'] - summary1['total_guarantee_balance'],
            "business_count_change": summary2['business_count'] - summary1['business_count'],
            "company_count_change": summary2['company_count'] - summary1['company_count']
        },
        "percentage_changes": percentage_changes,
        "company_analysis": {
            "new_companies": new_companies,
            "lost_companies": lost_companies,
            "continuing_companies": continuing_companies,
            "new_companies_count": len(new_companies),
            "lost_companies_count": len(lost_companies),
            "continuing_companies_count": len(continuing_companies),
            "new_companies_loan": new_companies_loan,
            "lost_companies_loan": lost_companies_loan,
            "continuing_companies_loan_change": continuing_companies_loan2 - continuing_companies_loan1
        }
    }
