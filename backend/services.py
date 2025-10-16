from collections import defaultdict
import pandas as pd
from models import db, BusinessData, DataHistory, QCCIndustry, QCCTech
from sqlalchemy import func
from datetime import datetime, timedelta
import logging
import time

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def read_sheet_data(file, sheet_name, header, columns, business_type, bank_name=None):

    raw_data = pd.read_excel(file, sheet_name=sheet_name, header=header)
    raw_data = raw_data[columns]
    raw_data['企业名称'] = raw_data['企业名称'].str.replace(r'[\s\n]+', '', regex=True)
    raw_data["业务类型"] = business_type
    if bank_name:
        raw_data["合作银行"] = bank_name
    return raw_data

def merge_qcc_data(raw_data):

    query_qcc_industry = QCCIndustry.query.all()
    qcc_industry_df = pd.DataFrame([d.to_dict() for d in query_qcc_industry])

    qcc_industry = qcc_industry_df[
        ['company_name', 'enterprise_scale', 'enterprise_type', 'national_standard_industry_category_main', 'national_standard_industry_category_major',
         'qcc_industry_category_main', 'qcc_industry_category_major']]
    qcc_industry = qcc_industry.drop_duplicates(subset='company_name')
    qcc_industry = qcc_industry.rename(columns={
        'company_name': '企业名称',
        'enterprise_scale': '企业规模',
        'enterprise_type': '企业（机构）类型',
        'national_standard_industry_category_main': '国标行业门类',
        'national_standard_industry_category_major': '国标行业大类',
        'qcc_industry_category_main': '企查查行业门类',
        'qcc_industry_category_major': '企查查行业大类'
    })

    query_qcc_tech = QCCTech.query.all()
    tech_data_df = pd.DataFrame([d.to_dict() for d in query_qcc_tech])

    tech_data = tech_data_df[['company_name', 'name', 'level']]
    tech_data = tech_data.rename(columns={
        'company_name': '企业名称',
        'name': '名称',
        'level': '级别'
    })

    tech_pivot = tech_data.pivot_table(index='企业名称', columns='名称', values='级别', aggfunc='count')
    tech_pivot = tech_pivot.reindex(columns=['专精特新“小巨人”企业', '专精特新中小企业', '高新技术企业', '创新型中小企业', '科技型中小企业']).fillna(0)
    tech_pivot = tech_pivot.reset_index()
    tech_pivot = tech_pivot.replace(1, '是').fillna('否')
    def is_tech(df):
        if df[['专精特新“小巨人”企业', '专精特新中小企业', '高新技术企业', '创新型中小企业', '科技型中小企业']].eq(
                '否').all():
            return '否'
        return '是'
    tech_pivot['科技企业'] = tech_pivot.apply(is_tech, axis=1)

    merged_data = pd.merge(raw_data, qcc_industry, on='企业名称', how='left')
    self_employed_individual_mask = ['企业规模','国标行业门类','企业（机构）类型','国标行业大类','企查查行业门类','企查查行业大类']
    merged_data.loc[~merged_data['企业名称'].str.contains('公司', na=False), self_employed_individual_mask] = '个体工商户'

    merged_data = pd.merge(merged_data, tech_pivot, on='企业名称', how='left')
    merged_data.update(merged_data[['专精特新“小巨人”企业', '专精特新中小企业', '高新技术企业', '创新型中小企业',
                                    '科技型中小企业', '科技企业']].fillna('否'))

    return merged_data


def read_data(file):

    data_1 = read_sheet_data(file, "线下业务", 1,
                             ["企业名称", "借款金额（万元）", "担保金额（万元）", "借款起始日", "借款到期日", "借款利率",
                              "担保费率", "借款余额（万元）", "担保余额（万元）", "借据状态", "结清日期", "企业划型",
                              "合作银行", "业务年度"], "常规业务")
    data_2 = read_sheet_data(file, "微众批量业务", 1,
                             ["企业名称", "借款金额（万元）", "借款起始日", "借款到期日", "借款利率", "担保费率",
                              "借款余额（万元）", "担保余额（万元）", "借据状态", "结清日期", "企业划型"], "微众批量业务",
                             "微众银行")
    data_3 = read_sheet_data(file, "建行批量业务", 1,
                             ["企业名称", "借款金额（万元）", "担保金额（万元）", "借款起始日", "借款到期日", "借款利率",
                              "担保费率", "借款余额（万元）", "担保余额（万元）", "借据状态", "结清日期", "企业划型",
                              "业务年度"], "建行批量业务", "建设银行")
    data_4 = read_sheet_data(file, "工行批量业务", 1,
                             ["企业名称", "借款金额（万元）", "担保金额（万元）", "借款起始日", "借款到期日", "借款利率",
                              "担保费率", "借款余额（万元）", "担保余额（万元）", "借据状态", "结清日期", "企业划型",
                              "业务年度"], "工行批量业务", "工商银行")

    if not data_2['借款起始日'].empty:
        data_2['借款起始日'] = pd.to_datetime(data_2['借款起始日'], errors='coerce')
        data_2["业务年度"] = data_2["借款起始日"].dt.year
    if not data_2['借款到期日'].empty:
        data_2['借款到期日'] = pd.to_datetime(data_2['借款到期日'], errors='coerce')
    if not data_2['结清日期'].empty:
        data_2['结清日期'] = pd.to_datetime(data_2['结清日期'], errors='coerce')

    data_2["担保金额（万元）"] = data_2["借款金额（万元）"] * 0.8

    # 合并数据
    result_total = pd.concat([data_1, data_2, data_3, data_4], ignore_index=True)

    result_total.dropna(subset="企业名称", inplace=True)
    result_total = result_total[result_total['企业名称'] != '/']
    result_total["业务年度"] = result_total["业务年度"].astype(int)
    result_total["企业划型"] = result_total["企业划型"].replace(
        {"微型企业": "微型", "小微企业": "小型", "小型企业": "小型", "中型企业": "中型", "大型企业": "大型"})
    result_total["借据状态"] = result_total["借据状态"].replace({"是": "已结清", "否": "正常"})

    result_total[["借款金额（万元）", "担保金额（万元）", "借款余额（万元）", "担保余额（万元）", "借款利率", "担保费率"]] = result_total[["借款金额（万元）", "担保金额（万元）", "借款余额（万元）", "担保余额（万元）", "借款利率", "担保费率"]].apply(lambda x: pd.to_numeric(x,errors='coerce'))
    result_total[["借款金额（万元）", "担保金额（万元）", "借款余额（万元）", "担保余额（万元）", "借款利率", "担保费率"]] = result_total[["借款金额（万元）", "担保金额（万元）", "借款余额（万元）", "担保余额（万元）", "借款利率", "担保费率"]].fillna(0)

    # 合并企查查和科技数据
    raw_data = merge_qcc_data(result_total)

    return raw_data


def import_data_from_excel(file, year, month):
    processed_data = read_data(file)
    processed_data.columns = processed_data.columns.str.strip()

    # Define all possible columns
    all_columns = [
        '企业名称', '借款金额（万元）', '担保金额（万元）', '借款起始日', '借款到期日', '借款利率',
        '担保费率', '借款余额（万元）', '担保余额（万元）', '借据状态', '结清日期', '企业划型',
        '合作银行', '业务年度', '业务类型', '企业规模', '企业（机构）类型', '国标行业门类',
        '国标行业大类', '企查查行业门类', '企查查行业大类', '专精特新“小巨人”企业',
        '专精特新中小企业', '高新技术企业', '创新型中小企业', '科技型中小企业', '科技企业'
    ]

    # Reindex the DataFrame to ensure all columns are present
    processed_data = processed_data.reindex(columns=all_columns)

    # Data Cleansing
    if '业务年度' not in processed_data.columns and '借款起始日' in processed_data.columns:
        processed_data['借款起始日'] = pd.to_datetime(processed_data['借款起始日'], errors='coerce')
        processed_data['业务年度'] = processed_data['借款起始日'].dt.year
    elif '业务年度' not in processed_data.columns:
        processed_data['业务年度'] = year

    numeric_cols = [
        '借款金额（万元）', '担保金额（万元）', '借款利率', '担保费率',
        '借款余额（万元）', '担保余额（万元）'
    ]
    for col in numeric_cols:
        processed_data[col] = pd.to_numeric(processed_data[col], errors='coerce').fillna(0)

    string_cols = [
        '企业名称', '借据状态', '企业划型', '合作银行', '业务类型', '企业规模', '企业（机构）类型',
        '国标行业门类', '国标行业大类', '企查查行业门类', '企查查行业大类'
    ]
    for col in string_cols:
        processed_data[col] = processed_data[col].fillna('')


    db.session.query(BusinessData).filter_by(snapshot_year=year, snapshot_month=month).delete()
    db.session.commit()

    for i, row in processed_data.iterrows():
        try:
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
                business_year_val = year

            new_data = BusinessData(
                company_name=row.get('企业名称'),
                loan_amount=float(row.get('借款金额（万元）')),
                guarantee_amount=float(row.get('担保金额（万元）')),
                loan_start_date=loan_start_date,
                loan_due_date=loan_due_date,
                loan_interest_rate=float(row.get('借款利率')),
                guarantee_fee_rate=float(row.get('担保费率')),
                outstanding_loan_balance=float(row.get('借款余额（万元）')),
                outstanding_guarantee_balance=float(row.get('担保余额（万元）')),
                loan_status=row.get('借据状态'),
                settlement_date=pd.to_datetime(row.get('结清日期')).date() if pd.notna(row.get('结清日期')) else None,
                enterprise_classification=row.get('企业划型'),
                cooperative_bank=row.get('合作银行'),
                snapshot_year=year,
                snapshot_month=month,
                business_year=business_year_val,
                business_type=row.get('业务类型'),
                enterprise_size=row.get('企业规模'),
                enterprise_institution_type=row.get('企业（机构）类型'),
                national_standard_industry_category_main=row.get('国标行业门类'),
                national_standard_industry_category_major=row.get('国标行业大类'),
                qichacha_industry_category_main=row.get('企查查行业门类'),
                qichacha_industry_category_major=row.get('企查查行业大类'),
                is_little_giant_enterprise=row.get('专精特新“小巨人”企业') == '是' if pd.notna(
                    row.get('专精特新“小巨人”企业')) else None,
                is_srun_sme=row.get('专精特新中小企业') == '是' if pd.notna(row.get('专精特新中小企业')) else None,
                is_high_tech_enterprise=row.get('高新技术企业') == '是' if pd.notna(row.get('高新技术企业')) else None,
                is_innovative_sme=row.get('创新型中小企业') == '是' if pd.notna(row.get('创新型中小企业')) else None,
                is_tech_based_sme=row.get('科技型中小企业') == '是' if pd.notna(row.get('科技型中小企业')) else None,
                is_technology_enterprise=row.get('科技企业') == '是' if pd.notna(row.get('科技企业')) else None
            )
            logger.info(f"Inserting row {i}: {new_data.__dict__}")
            db.session.add(new_data)
            if (i + 1) % 1000 == 0:
                try:
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    logger.error(f"Error committing chunk to database: {e}", exc_info=True)
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error processing row {i}: {row.to_dict()}", exc_info=True)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error during final commit: {e}", exc_info=True)

    logger.info(f"{file.filename}: All data processed.")


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
    if 'loan_status' in df_current.columns:
        df_current = df_current[~(df_current['loan_status'] == '未放款')]

    if df_current.empty:
        return {
            "cumulative_loan_amount": 0,
            "cumulative_guarantee_amount": 0,
            "cumulative_guaranteed_company_count": 0,
            "new_guaranteed_companies_this_year_count": 0,
            "new_companies_this_year_loan": 0,
            "new_companies_this_year_guarantee": 0,
            "in_force_companies_count": 0,
            "total_loan_balance": 0,
            "total_guarantee_balance": 0,
        }

    cumulative_loan_amount = df_current['loan_amount'].sum()
    cumulative_guarantee_amount = df_current['guarantee_amount'].sum()
    cumulative_guaranteed_company_count = df_current[df_current['guarantee_amount'] > 0]['company_name'].nunique()
    new_guaranteed_companies_this_year_count = df_current[(df_current['business_year'] == year) & (df_current['guarantee_amount'] > 0)]['company_name'].nunique()
    new_companies_this_year_loan = df_current[df_current['business_year'] == year]['loan_amount'].sum()
    new_companies_this_year_gurantee = df_current[df_current['business_year'] == year]['guarantee_amount'].sum()
    in_force_companies_count = df_current[df_current['outstanding_guarantee_balance'] > 0]['company_name'].nunique()
    total_loan_balance = df_current['outstanding_loan_balance'].sum()
    total_guarantee_balance = df_current['outstanding_guarantee_balance'].sum()

    result = {
        'cumulative_loan_amount': float(cumulative_loan_amount),
        'cumulative_guarantee_amount': float(cumulative_guarantee_amount),
        'cumulative_guaranteed_company_count': int(cumulative_guaranteed_company_count),
        'new_guaranteed_companies_this_year_count': int(new_guaranteed_companies_this_year_count),
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
    if 'loan_status' in df1.columns:
        df1 = df1[~(df1['loan_status'] == '未放款')]

    data2 = BusinessData.query.filter_by(snapshot_year=year2, snapshot_month=month2).all()
    df2 = pd.DataFrame([d.to_dict() for d in data2])
    if 'loan_status' in df2.columns:
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
    if 'loan_status' in df_current.columns:
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
        if 'loan_status' in df_year_current_snapshot.columns:
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
                yearly_summaries[int(y)][bt]['in_force_companies_count'] = df_filtered_year_current[df_filtered_year_current['outstanding_guarantee_balance'] > 0]['company_name'].nunique()
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
            yearly_summaries[int(y)]['merged_unique_company_count_in_force'] = df_year_current_snapshot[df_year_current_snapshot['outstanding_guarantee_balance'] > 0]['company_name'].nunique()

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

    # Calculate grand totals
    grand_total_loan_amount = df_overall['loan_amount'].sum()
    grand_total_companies = df_overall['company_name'].nunique()

    return {
        "money_results": money_results,
        "num_results": num_results,
        "grand_total_loan_amount": float(grand_total_loan_amount),
        "grand_total_companies": int(grand_total_companies)
    }


def get_average_amounts(year, month):
    # Get the base query for the selected snapshot
    query = db.session.query(
        BusinessData.business_type,
        func.avg(BusinessData.loan_amount).label('avg_loan_amount'),
        func.avg(BusinessData.guarantee_amount).label('avg_guarantee_amount'),
        func.max(BusinessData.loan_amount).label('max_loan_amount'),
        func.min(BusinessData.loan_amount).label('min_loan_amount')
    ).filter(
        BusinessData.snapshot_year == year,
        BusinessData.snapshot_month == month
    ).group_by(BusinessData.business_type)

    results_by_type = query.all()

    # Calculate overall averages
    overall_query = db.session.query(
        func.avg(BusinessData.loan_amount).label('overall_avg_loan'),
        func.avg(BusinessData.guarantee_amount).label('overall_avg_guarantee')
    ).filter(
        BusinessData.snapshot_year == year,
        BusinessData.snapshot_month == month
    )
    overall_results = overall_query.one()

    business_types = ['常规业务', '建行批量业务', '微众批量业务', '工行批量业务']
    response_data = {
        'by_type': {},
        'overall': {
            'avg_loan_amount': float(overall_results.overall_avg_loan) if overall_results.overall_avg_loan else 0,
            'avg_guarantee_amount': float(overall_results.overall_avg_guarantee) if overall_results.overall_avg_guarantee else 0
        }
    }

    for r in results_by_type:
        if r.business_type in business_types:
            response_data['by_type'][r.business_type] = {
                'avg_loan_amount': float(r.avg_loan_amount) if r.avg_loan_amount else 0,
                'avg_guarantee_amount': float(r.avg_guarantee_amount) if r.avg_guarantee_amount else 0,
                'max_loan_amount': float(r.max_loan_amount) if r.max_loan_amount else 0,
                'min_loan_amount': float(r.min_loan_amount) if r.min_loan_amount else 0,
            }

    # Ensure all business types are in the response
    for bt in business_types:
        if bt not in response_data['by_type']:
            response_data['by_type'][bt] = {
                'avg_loan_amount': 0,
                'avg_guarantee_amount': 0,
                'max_loan_amount': 0,
                'min_loan_amount': 0,
            }

    return response_data


def get_due_date_summary(year, month):
    from sqlalchemy import extract, case

    # Base query for the selected snapshot
    base_query = BusinessData.query.filter(
        BusinessData.snapshot_year == year,
        BusinessData.snapshot_month == month,
        BusinessData.loan_due_date.isnot(None)
    )

    # We need data for years 2024, 2025, 2026
    results = base_query.filter(
        extract('year', BusinessData.loan_due_date).in_([2024, 2025, 2026])
    ).all()

    if not results:
        return {}

    df = pd.DataFrame([r.to_dict() for r in results])
    df['loan_due_date'] = pd.to_datetime(df['loan_due_date'])

    # Create year and month columns from loan_due_date
    df['due_year'] = df['loan_due_date'].dt.year
    df['due_month'] = df['loan_due_date'].dt.month

    # Differentiate weizhong and non-weizhong
    df['weizhong_amount'] = df.apply(
        lambda row: row['loan_amount'] if row['business_type'] == '微众批量业务' else 0,
        axis=1
    )
    df['non_weizhong_amount'] = df.apply(
        lambda row: row['loan_amount'] if row['business_type'] != '微众批量业务' else 0,
        axis=1
    )

    # Group by year and month
    summary = df.groupby(['due_year', 'due_month'])[['weizhong_amount', 'non_weizhong_amount']].sum().reset_index()

    # Format the data for the frontend
    response_data = {}
    for year_to_process in [2024, 2025, 2026]:
        year_data = summary[summary['due_year'] == year_to_process]
        
        # Create a dataframe with all 12 months
        months_df = pd.DataFrame({'due_month': range(1, 13)})
        
        # Merge with year_data to fill missing months with 0
        merged_data = pd.merge(months_df, year_data, on='due_month', how='left').fillna(0)
        
        response_data[str(year_to_process)] = merged_data.to_dict('records')

    return response_data


def get_balance_projection(year, month):
    from dateutil.relativedelta import relativedelta

    # Get the data from the selected snapshot
    loans = BusinessData.query.filter_by(snapshot_year=year, snapshot_month=month).all()
    if not loans:
        return []

    # Generate the date range for the projection
    start_date = datetime(datetime.now().year, datetime.now().month, 1)
    end_date = datetime(2026, 12, 31)
    date_list = []
    current_date = start_date
    while current_date <= end_date:
        date_list.append(current_date)
        current_date += relativedelta(months=1)

    # Calculate the projected balances
    projection_data = []
    for projection_date in date_list:
        total_loan_balance = 0
        total_guarantee_balance = 0
        for loan in loans:
            if loan.loan_due_date and loan.loan_due_date > projection_date.date():
                total_loan_balance += loan.outstanding_loan_balance if loan.outstanding_loan_balance else 0
                total_guarantee_balance += loan.outstanding_guarantee_balance if loan.outstanding_guarantee_balance else 0
        
        projection_data.append({
            'date': projection_date.strftime('%Y-%m'),
            'loan_balance': float(total_loan_balance),
            'guarantee_balance': float(total_guarantee_balance)
        })

    return projection_data


def import_qcc_industry(file):
    # Read the entire Excel file into a single DataFrame
    df = pd.read_excel(file, engine='openpyxl')
    db.session.query(QCCIndustry).delete()
    logger.info("QCCIndustry table truncated.")

    logger.info(f"Processing DataFrame with shape: {df.shape}")
    column_mapping = {
        '企业名称': 'company_name',
        '企业规模': 'enterprise_scale',
        '企业（机构）类型': 'enterprise_type',
        '国标行业门类': 'national_standard_industry_category_main',
        '国标行业大类': 'national_standard_industry_category_major',
        '企查查行业门类': 'qcc_industry_category_main',
        '企查查行业大类': 'qcc_industry_category_major',
    }
    df = df.rename(columns=column_mapping)

    # Use to_dict('records') for more efficient iteration
    records = df.to_dict('records')
    
    # Bulk insert for better performance
    db.session.bulk_insert_mappings(QCCIndustry, records)
    
    try:
        db.session.commit()
        logger.info(f"Committed {len(records)} records to the database.")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to commit records to database: {e}", exc_info=True)
        raise e

    logger.info("All records processed and committed successfully.")

def import_qcc_tech(file):
    try:
        chunk_iter = pd.read_csv(file, chunksize=1000)
        db.session.query(QCCTech).delete()

        for chunk in chunk_iter:
            column_mapping = {
                '企业名称': 'company_name',
                '名称': 'name',
                '荣誉类型': 'honor_type',
                '级别': 'level',
            }
            chunk = chunk.rename(columns=column_mapping)

            for _, row in chunk.iterrows():
                new_entry = QCCTech(
                    company_name=row.get('company_name'),
                    name=row.get('name'),
                    honor_type=row.get('honor_type'),
                    level=row.get('level'),
                )
                db.session.add(new_entry)

            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                raise e

    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to import QCC Tech data: {e}", exc_info=True)
        raise e

def get_monthly_growth(year, month):
    # Filter for the current snapshot data
    current_snapshot_data = BusinessData.query.filter_by(snapshot_year=year, snapshot_month=month).all()
    df_current = pd.DataFrame([d.to_dict() for d in current_snapshot_data])
    if 'loan_status' in df_current.columns:
        df_current = df_current[~(df_current['loan_status'] == '未放款')]

    if df_current.empty:
        return {
            "new_loan_amount": 0,
            "new_guarantee_amount": 0,
            "new_guaranteed_company_count": 0,
        }

    # Calculate monthly growth
    df_current['loan_start_date'] = pd.to_datetime(df_current['loan_start_date'])
    new_loan_amount = df_current[(df_current['business_year'] == year) & (df_current['loan_start_date'].dt.month == month)]['loan_amount'].sum()
    new_guarantee_amount = df_current[(df_current['business_year'] == year) & (df_current['loan_start_date'].dt.month == month)]['guarantee_amount'].sum()
    new_guaranteed_company_count = df_current[(df_current['business_year'] == year) & (df_current['loan_start_date'].dt.month == month) & (df_current['guarantee_amount'] > 0)]['company_name'].nunique()

    result = {
        'new_loan_amount': float(new_loan_amount),
        'new_guarantee_amount': float(new_guarantee_amount),
        'new_guaranteed_company_count': int(new_guaranteed_company_count),
    }
    return result