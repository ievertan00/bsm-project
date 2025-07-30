from collections import defaultdict

import pandas as pd
from models import db, BusinessData, DataHistory
from sqlalchemy import func
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def import_data_from_excel(file, year, month):
    df = pd.read_excel(file)
    df.columns = df.columns.str.strip()  # Strip whitespace from column names

    # Data Cleansing: If '业务年度' is missing, derive from '借款起始日'
    if '业务年度' not in df.columns and '借款起始日' in df.columns:
        # Ensure date column is in datetime format
        df['借款起始日'] = pd.to_datetime(df['借款起始日'], errors='coerce')
        df['业务年度'] = df['借款起始日'].dt.year
    elif '业务年度' not in df.columns:
        df['业务年度'] = year  # Fallback to snapshot year

    # Inspect and assign 0 for empty numeric data
    numeric_cols_to_fill_zero = [
        '借款金额（万元）',
        '担保金额（万元）',
        '借款利率',
        '担保费率',
        '借款余额（万元）',
        '担保余额（万元）'
    ]
    for col in numeric_cols_to_fill_zero:
        if col in df.columns:
            # Convert to numeric, coercing errors to NaN, then fill NaN with 0
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # Delete existing data for the specified year and month
    db.session.query(BusinessData).filter_by(snapshot_year=year, snapshot_month=month).delete()
    db.session.commit()  # Commit the deletion before adding new data

    for _, row in df.iterrows():
        company_name = row.get('企业名称')
        loan_start_date = pd.to_datetime(row.get('借款起始日')).date() if pd.notna(row.get('借款起始日')) else None
        loan_due_date = pd.to_datetime(row.get('借款到期日')).date() if pd.notna(row.get('借款到期日')) else None

        business_year_val = None
        if '业务年度' in row and pd.notna(row.get('业务年度')):
            try:
                business_year_val = int(row.get('业务年度'))
            except (ValueError, TypeError):
                business_year_val = loan_start_date.year if loan_start_date else year
        elif loan_start_date:
            business_year_val = loan_start_date.year
        else:
            business_year_val = year  # Fallback to snapshot year

        # These are now handled by the DataFrame-level cleaning
        loan_interest_rate_val = row.get('借款利率')
        guarantee_fee_rate_val = row.get('担保费率')

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
            business_year=business_year_val,
            business_type=row.get('业务类型'),
            enterprise_size=row.get('企业规模'),
            establishment_date=pd.to_datetime(row.get('成立日期')).date() if pd.notna(row.get('成立日期')) else None,
            enterprise_institution_type=row.get('企业（机构）类型'),
            national_standard_industry_category_main=row.get('国标行业门类'),
            national_standard_industry_category_major=row.get('国标行业大类'),
            qichacha_industry_category_main=row.get('企查查行业门类'),
            qichacha_industry_category_major=row.get('企查查行业大类'),
            is_little_giant_enterprise=bool(row.get('专精特新“小巨人”企业')) if pd.notna(
                row.get('专精特新“小巨人”企业')) else None,
            is_srun_sme=bool(row.get('专精特新中小企业')) if pd.notna(row.get('专精特新中小企业')) else None,
            is_high_tech_enterprise=bool(row.get('高新技术企业')) if pd.notna(row.get('高新技术企业')) else None,
            is_innovative_sme=bool(row.get('创新型中小企业')) if pd.notna(row.get('创新型中小企业')) else None,
            is_tech_based_sme=bool(row.get('科技型中小企业')) if pd.notna(row.get('科技型中小企业')) else None,
            is_technology_enterprise=bool(row.get('科技企业')) if pd.notna(row.get('科技企业')) else None
        )
        try:
            db.session.add(new_data)
            db.session.commit()
            logger.debug(f"Successfully added row for company: {company_name}")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error adding row to database for company {company_name}: {row.to_dict()}. Error: {e}", exc_info=True)
            raise Exception(f"Database insertion failed for a row. Check logs for details. Error: {e}")
    logger.info(f"{file.filename}: All data processed and committed successfully.")


def get_statistics(year=None, month=None, business_type=None, cooperative_bank=None, is_technology_enterprise=None):
    query = BusinessData.query.filter_by(snapshot_year=year, snapshot_month=month)

    if business_type:
        query = query.filter_by(business_type=business_type)
    if cooperative_bank:
        query = query.filter_by(cooperative_bank=cooperative_bank)
    if is_technology_enterprise is not None:
        query = query.filter_by(is_technology_enterprise=is_technology_enterprise)

    current_snapshot_data = query.all()
    df_current = pd.DataFrame([d.to_dict() for d in current_snapshot_data])
    df_current = df_current[~(df_current['loan_status'] == '未放款')]

    if df_current.empty:
        return {
            "cumulative_loan_amount": 0,
            "cumulative_guarantee_amount": 0,
            "cumulative_company_count": 0,
            "new_companies_this_year_count": 0,
            "new_companies_this_year_loan": 0,
            "new_companies_this_year_guarantee": 0,
            "in_force_companies_count": 0,
            "total_loan_balance": 0,
            "total_guarantee_balance": 0,
        }

    cumulative_loan_amount = df_current['loan_amount'].sum()
    cumulative_guarantee_amount = df_current['guarantee_amount'].sum()
    cumulative_company_count = df_current['company_name'].nunique()
    new_companies_this_year_count = df_current[df_current['business_year'] == year]['company_name'].nunique()
    new_companies_this_year_loan = df_current[df_current['business_year'] == year]['loan_amount'].sum()
    new_companies_this_year_gurantee = df_current[df_current['business_year'] == year]['guarantee_amount'].sum()
    in_force_companies_count = df_current[df_current['outstanding_loan_balance'] > 0]['company_name'].nunique()
    total_loan_balance = df_current['outstanding_loan_balance'].sum()
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

    new_data.pop('id', None)
    new_data.pop('created_at', None)

    for key, value in new_data.items():
        if key in ['loan_start_date', 'loan_due_date', 'settlement_date', 'establishment_date']:
            value = datetime.strptime(value, '%Y-%m-%d').date() if value else None
        elif key in ['loan_amount', 'guarantee_amount', 'outstanding_loan_balance', 'outstanding_guarantee_balance',
                    'loan_interest_rate', 'guarantee_fee_rate']:
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
    df1 = df1[~(df1['loan_status'] == '未放款')]

    data2 = BusinessData.query.filter_by(snapshot_year=year2, snapshot_month=month2).all()
    df2 = pd.DataFrame([d.to_dict() for d in data2])
    df2 = df2[~(df2['loan_status'] == '未放款')]

    def get_safe_sum(df, column):
        if not df.empty and column in df.columns:
            return df[column].fillna(0).sum()
        return 0.0

    def get_safe_unique_count(df, column):
        if not df.empty and column in df.columns:
            return df[column].nunique()
        return 0

    def get_this_year_sum(df, column, year):
        if not df.empty and column in df.columns and 'business_year' in df.columns:
            df['business_year'] = pd.to_numeric(df['business_year'], errors='coerce')
            return df[df['business_year'] == year][column].fillna(0).sum()
        return 0.0

    def get_this_year_count(df, column, year):
        if not df.empty and column in df.columns and 'business_year' in df.columns:
            df['business_year'] = pd.to_numeric(df['business_year'], errors='coerce')
            return df[df['business_year'] == year][column].nunique()
        return 0

    if df1.empty:
        return {"error": f"Data not available for {year_month1}."}
    if df2.empty:
        return {"error": f"Data not available for {year_month2}."}

    summary_keys = [
        "total_loan_amount", "total_guarantee_amount",
        "new_companies_this_year_loan", "new_companies_this_year_guarantee_amount",
        "total_loan_balance", "total_guarantee_balance",
        "business_count", "company_count", "new_companies_this_year_count"
    ]

    def create_summary(df, year):
        summary = {
            "total_loan_amount": get_safe_sum(df, 'loan_amount'),
            "total_guarantee_amount": get_safe_sum(df, 'guarantee_amount'),
            "new_companies_this_year_loan": get_this_year_sum(df, 'loan_amount', year),
            "new_companies_this_year_guarantee_amount": get_this_year_sum(df, 'guarantee_amount', year),
            "total_loan_balance": get_safe_sum(df, 'outstanding_loan_balance'),
            "total_guarantee_balance": get_safe_sum(df, 'outstanding_guarantee_balance'),
            "business_count": len(df),
            "company_count": get_safe_unique_count(df, 'company_name'),
            "new_companies_this_year_count": get_this_year_count(df, 'company_name', year),
        }
        for key, value in summary.items():
            if 'count' in key:
                summary[key] = int(value)
            else:
                summary[key] = float(value)
        return summary

    summary1 = create_summary(df1, year1)
    summary2 = create_summary(df2, year2)

    def calculate_percentage_change(old, new):
        if old is None or new is None: return 0.0
        if old == 0:
            return 999999.0 if new > 0 else 0.0
        return ((new - old) / old) * 100

    changes = {f"{key}_change": (summary2.get(key, 0) or 0) - (summary1.get(key, 0) or 0) for key in summary_keys}
    percentage_changes = {key: calculate_percentage_change(summary1.get(key), summary2.get(key)) for key in summary_keys}

    companies1 = set(df1['company_name'].dropna().unique()) if 'company_name' in df1.columns else set()
    companies2 = set(df2['company_name'].dropna().unique()) if 'company_name' in df2.columns else set()

    new_company_names = list(companies2 - companies1)

    new_companies_df = df2[df2['company_name'].isin(new_company_names)]
    new_companies_details = new_companies_df.to_dict('records')

    lost_companies_names = list(companies1 - companies2)
    continuing_companies_names = list(companies1.intersection(companies2))

    new_companies_loan = get_safe_sum(new_companies_df, 'loan_amount')
    lost_companies_loan = get_safe_sum(df1[df1['company_name'].isin(lost_companies_names)], 'loan_amount')
    continuing_companies_loan1 = get_safe_sum(df1[df1['company_name'].isin(continuing_companies_names)], 'loan_amount')
    continuing_companies_loan2 = get_safe_sum(df2[df2['company_name'].isin(continuing_companies_names)], 'loan_amount')

    return {
        "summary1": summary1,
        "summary2": summary2,
        "changes": changes,
        "percentage_changes": percentage_changes,
        "company_analysis": {
            "new_companies": new_companies_details,
            "lost_companies": lost_companies_names,
            "continuing_companies": continuing_companies_names,
            "new_companies_count": len(new_company_names),
            "lost_companies_count": len(lost_companies_names),
            "continuing_companies_count": len(continuing_companies_names),
            "new_companies_loan": float(new_companies_loan),
            "lost_companies_loan": float(lost_companies_loan),
            "continuing_companies_loan_change": float(continuing_companies_loan2 - continuing_companies_loan1)
        }
    }

def get_slicer_options():
    business_types = [item[0] for item in db.session.query(BusinessData.business_type).distinct().all() if item[0] is not None]
    cooperative_banks = [item[0] for item in db.session.query(BusinessData.cooperative_bank).distinct().all() if item[0] is not None]
    
    # Technology enterprise options
    is_technology_enterprise_options = [
        {"label": "所有", "value": "all"},
        {"label": "是", "value": True},
        {"label": "否", "value": False}
    ]

    return {
        "business_types": sorted(business_types),
        "cooperative_banks": sorted(cooperative_banks),
        "is_technology_enterprise_options": is_technology_enterprise_options
    }

def get_all_business_data(page, per_page, company_name=None, year=None, month=None, business_type=None, cooperative_bank=None, is_technology_enterprise=None):
    query = BusinessData.query

    if year and month:
        query = query.filter_by(snapshot_year=year, snapshot_month=month)
    
    if company_name:
        query = query.filter(BusinessData.company_name.ilike(f'%{company_name}%'))

    if business_type:
        query = query.filter_by(business_type=business_type)
    if cooperative_bank:
        query = query.filter_by(cooperative_bank=cooperative_bank)
    if is_technology_enterprise is not None:
        if is_technology_enterprise == "N/A":
            query = query.filter(BusinessData.is_technology_enterprise.is_(None))
        else:
            query = query.filter_by(is_technology_enterprise=is_technology_enterprise)

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return {
        "data": [item.to_dict() for item in pagination.items],
        "current_page": pagination.page,
        "pages": pagination.pages,
        "total": pagination.total,
    }

def get_detailed_statistics(year, month):

    # Filter for the current snapshot data
    current_snapshot_data = BusinessData.query.filter_by(snapshot_year=year, snapshot_month=month).all()
    df_current = pd.DataFrame([d.to_dict() for d in current_snapshot_data])
    df_current = df_current[~(df_current['loan_status'] == '未放款')]

    # Ensure business_type column exists and fill NaN
    if 'business_type' not in df_current.columns:
        df_current['business_type'] = '未知业务'
    df_current['business_type'] = df_current['business_type'].fillna('未知业务')

    business_types_to_report = ['常规业务', '建行批量业务', '微众批量业务', '工行批量业务']
    
    results = {bt: {} for bt in business_types_to_report}
    results['合计'] = defaultdict(int)

    # Calculate for each business type
    for bt in business_types_to_report:
        df_filtered_current = df_current[df_current['business_type'] == bt]

        results[bt]['loan_amount'] = df_filtered_current['loan_amount'].sum()
        results[bt]['guarantee_amount'] = df_filtered_current['guarantee_amount'].sum()
        results[bt]['company_count'] = df_filtered_current['company_name'].nunique()
        results[bt]['in_force_companies_count'] = df_filtered_current[df_filtered_current['outstanding_guarantee_balance'] > 0]['company_name'].nunique()
        results[bt]['loan_balance'] = df_filtered_current['outstanding_loan_balance'].sum()
        results[bt]['guarantee_balance'] = df_filtered_current['outstanding_guarantee_balance'].sum()
        
        # Cumulative company count across years for this business type
        results[bt]['cumulative_company_count'] = df_filtered_current['company_name'].nunique()

        results['合计']['company_count'] += df_filtered_current['company_name'].nunique()
        results['合计']['cumulative_company_count'] += df_filtered_current['company_name'].nunique()
        results['合计']['in_force_companies_count'] += df_filtered_current[df_filtered_current['outstanding_guarantee_balance'] > 0]['company_name'].nunique()

    results['合计']['loan_amount'] = df_current['loan_amount'].sum()
    results['合计']['guarantee_amount'] = df_current['guarantee_amount'].sum()
    results['合计']['guarantee_balance'] = df_current['outstanding_guarantee_balance'].sum()
    results['合计']['loan_balance'] = df_current['outstanding_loan_balance'].sum()

    # Add merged unique counts for specific columns
    results['merged_unique_company'] = df_current['company_name'].nunique()
    results['merged_cumlative_unique_company'] = df_current['company_name'].nunique()
    results['merged_unique_company_count_in_force'] = df_current[df_current['outstanding_guarantee_balance'] > 0]['company_name'].nunique()

    # Ensure all values are floats
    for bt_key in results:
        if isinstance(results[bt_key], dict):
            for stat_key in results[bt_key]:
                results[bt_key][stat_key] = float(results[bt_key][stat_key])


    # Prepare data for yearly summaries
    yearly_summaries = {}
    years = list(range(2021, 2031))
    all_years = sorted([y for y in years if y <=year], reverse=True)

    for y in all_years:
        # Fetch all data up to the selected year and month for cumulative calculations
        if y == year:
            historical_data = BusinessData.query.filter(
                (BusinessData.snapshot_year == y) & (BusinessData.snapshot_month == month)
            ).all()
            df_all_cumulative = pd.DataFrame([d.to_dict() for d in historical_data])


        else:
            historical_data = BusinessData.query.filter(
                (BusinessData.snapshot_year == y) & (BusinessData.snapshot_month == 12)
            ).all()
            df_all_cumulative = pd.DataFrame([d.to_dict() for d in historical_data])

        # Data for the current year (up to the selected month if it's the current year)
        df_year_current_snapshot = df_all_cumulative.copy()
        df_year_current_snapshot = df_year_current_snapshot[~(df_year_current_snapshot['loan_status'] == '未放款')]

        if 'business_type' not in df_year_current_snapshot.columns:
            df_year_current_snapshot['business_type'] = '未知业务'
        df_year_current_snapshot['business_type'] = df_year_current_snapshot['business_type'].fillna('未知业务')

        yearly_summaries[int(y)] = {bt: {} for bt in business_types_to_report}
        yearly_summaries[int(y)]['合计'] = defaultdict(int)

        if not df_year_current_snapshot.empty:

            for bt in business_types_to_report:

                df_filtered_year_current = df_year_current_snapshot[df_year_current_snapshot['business_type'] == bt]

                yearly_summaries[int(y)][bt]['loan_amount'] = df_filtered_year_current[df_filtered_year_current['business_year'] == y]['loan_amount'].sum()
                yearly_summaries[int(y)][bt]['guarantee_amount'] = df_filtered_year_current[df_filtered_year_current['business_year'] == y]['guarantee_amount'].sum()
                yearly_summaries[int(y)][bt]['company_count'] = df_filtered_year_current[df_filtered_year_current['business_year'] == y]['company_name'].nunique()
                yearly_summaries[int(y)][bt]['in_force_companies_count'] = df_filtered_year_current[df_filtered_year_current['outstanding_loan_balance'] > 0]['company_name'].nunique()
                yearly_summaries[int(y)][bt]['loan_balance'] = df_filtered_year_current['outstanding_loan_balance'].sum()
                yearly_summaries[int(y)][bt]['guarantee_balance'] = df_filtered_year_current['outstanding_guarantee_balance'].sum()
                yearly_summaries[int(y)][bt]['cumulative_company_count'] = df_filtered_year_current['company_name'].nunique()

                yearly_summaries[int(y)]['合计']['company_count'] += yearly_summaries[int(y)][bt]['company_count']
                yearly_summaries[int(y)]['合计']['in_force_companies_count'] += yearly_summaries[int(y)][bt]['in_force_companies_count']
                yearly_summaries[int(y)]['合计']['cumulative_company_count'] += yearly_summaries[int(y)][bt]['cumulative_company_count']

            # Yearly total
            yearly_summaries[int(y)]['合计']['loan_amount'] = df_year_current_snapshot[df_year_current_snapshot['business_year'] == y]['loan_amount'].sum()
            yearly_summaries[int(y)]['合计']['guarantee_amount'] = df_year_current_snapshot[df_year_current_snapshot['business_year'] == y]['guarantee_amount'].sum()
            yearly_summaries[int(y)]['合计']['loan_balance'] = df_year_current_snapshot['outstanding_loan_balance'].sum()
            yearly_summaries[int(y)]['合计']['guarantee_balance'] = df_year_current_snapshot['outstanding_guarantee_balance'].sum()

            # Yearly merged unique counts
            yearly_summaries[int(y)]['merged_unique_company'] = df_year_current_snapshot[df_year_current_snapshot['business_year'] == y]['company_name'].nunique()
            yearly_summaries[int(y)]['merged_cumlative_unique_company'] = df_year_current_snapshot['company_name'].nunique()
            yearly_summaries[int(y)]['merged_unique_company_count_in_force'] = df_year_current_snapshot[df_year_current_snapshot['outstanding_loan_balance'] > 0]['company_name'].nunique()

            for bt_key in yearly_summaries[int(y)]:
                if isinstance(yearly_summaries[int(y)][bt_key], dict):
                    for stat_key in yearly_summaries[int(y)][bt_key]:
                        yearly_summaries[int(y)][bt_key][stat_key] = float(yearly_summaries[int(y)][bt_key][stat_key])

    return {
        "overall_summary": results, # This is the original 'results' for the selected month
        "yearly_summaries": yearly_summaries
    }

def get_overall_summary(year, month):
    current_snapshot_data = BusinessData.query.filter_by(snapshot_year=year, snapshot_month=month).all()
    df_overall = pd.DataFrame([d.to_dict() for d in current_snapshot_data])


    business_types = ['常规业务', '建行批量业务', '微众批量业务', '工行批量业务']
    years = [2021, 2022, 2023, 2024, 2025]

    # 初始化结果存储字典
    money_results = {}
    num_results = {}

    # 计算借款金额和唯一企业数量
    for y in years:
        v1 = {}
        v2 = {}
        for biz_type in business_types:
            # 计算借款金额
            v1[biz_type] = df_overall[
                (df_overall['business_type'] == biz_type) & (df_overall['business_year'] == y)]['loan_amount'].sum()

            # 计算唯一企业数量
            v2[biz_type] = df_overall[
                (df_overall['business_type'] == biz_type) & (df_overall['business_year'] == y)
                ]['company_name'].nunique()
        money_results[str(y)] = v1
        num_results[str(y)] = v2

    v3 = {}
    v4 = {}
    for biz_type in business_types:
        v3[biz_type] = df_overall[df_overall['business_type'] == biz_type]['loan_amount'].sum()
        v4[biz_type] = df_overall[df_overall['business_type'] == biz_type]['company_name'].nunique()

    money_results['total'] = v3
    num_results['total'] = v4

    return {
        "money_results": money_results,
        "num_results": num_results
    }
