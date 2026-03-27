from collections import defaultdict
from fastapi import HTTPException
import pandas as pd
import io
import datetime
from decimal import Decimal
from sqlalchemy import or_, func
from sqlalchemy.orm import Session
import crud
import models

def read_sheet_data(excel_source, sheet_name, header, columns, business_type, bank_name=None):
    try:
        if isinstance(excel_source, pd.ExcelFile):
            sheet_names = excel_source.sheet_names
        else:
            xl = pd.ExcelFile(excel_source)
            sheet_names = xl.sheet_names
            excel_source = xl

        actual_sheet_name = None
        for s in sheet_names:
            if s.strip() == sheet_name:
                actual_sheet_name = s
                break
        
        if not actual_sheet_name:
            return pd.DataFrame(columns=columns)

        raw_data = pd.read_excel(excel_source, sheet_name=actual_sheet_name, header=header)
        existing_cols = [col for col in columns if col in raw_data.columns]
        raw_data = raw_data[existing_cols]
        
        if '企业名称' in raw_data.columns:
            raw_data['企业名称'] = raw_data['企业名称'].astype(str).str.replace(r'[\s\n]+', '', regex=True)
            raw_data = raw_data[raw_data['企业名称'].notnull() & (raw_data['企业名称'] != 'nan') & (raw_data['企业名称'].str.strip() != "")]
        
        raw_data["业务类型"] = business_type
        if bank_name:
            raw_data["合作银行"] = bank_name
        
        return raw_data
    except Exception:
        return pd.DataFrame(columns=columns)

def get_or_create_company(db: Session, company_name: str) -> models.Company:
    company = db.query(models.Company).filter_by(company_name=company_name).first()
    if not company:
        company = models.Company(company_name=company_name)
        db.add(company)
        db.flush()
    return company

def merge_qcc_data(df, db: Session):
    # This logic now prepares attributes for the Company table
    companies = df['企业名称'].unique().tolist()
    if not companies:
        return df

    industries = {i.company_name: i for i in db.query(models.QCCIndustry).filter(models.QCCIndustry.company_name.in_(companies)).all()}
    techs = {t.company_name: t for t in db.query(models.QCCTech).filter(models.QCCTech.company_name.in_(companies)).all()}
    qyjh = {e.company_name: e for e in db.query(models.QYJHList).filter(models.QYJHList.company_name.in_(companies)).all()}

    def apply_qcc(row):
        name = row['企业名称']
        ind = industries.get(name)
        tech = techs.get(name)
        qyjh_item = qyjh.get(name)
        
        if ind:
            row['企业规模'] = ind.enterprise_scale
            row['企业（机构）类型'] = ind.enterprise_type
            row['国标行业门类'] = ind.national_standard_industry_category_main
            row['国标行业大类'] = ind.national_standard_industry_category_major
            row['企查查行业门类'] = ind.qcc_industry_category_main
            row['企查查行业大类'] = ind.qcc_industry_category_major

        if tech:
            row['专精特新“小巨人”企业'] = '是' if tech.is_little_giant_enterprise else '否'
            row['专精特新中小企业'] = '是' if tech.is_srun_sme else '否'
            row['高新技术企业'] = '是' if tech.is_high_tech_enterprise else '否'
            row['创新型中小企业'] = '是' if tech.is_innovative_sme else '否'
            row['科技型中小企业'] = '是' if tech.is_tech_based_sme else '否'

        row['千亿计划'] = qyjh_item.qyjh_category if qyjh_item else None
        is_tech = any(row.get(c) == '是' for c in ['专精特新“小巨人”企业', '专精特新中小企业', '高新技术企业', '创新型中小企业', '科技型中小企业']) or pd.notna(row['千亿计划'])
        row['科技企业'] = '是' if is_tech else '否'
        
        return row

    return df.apply(apply_qcc, axis=1)

def sync_all_business_data(db: Session):
    # Synchronize all Company records with latest master data
    companies = db.query(models.Company).all()
    if not companies:
        return 0

    count = 0
    for company in companies:
        # Industry
        ind = db.query(models.QCCIndustry).filter_by(company_name=company.company_name).first()
        if ind:
            company.enterprise_size = ind.enterprise_scale
            company.enterprise_institution_type = ind.enterprise_type
            company.national_standard_industry_category_main = ind.national_standard_industry_category_main
            company.national_standard_industry_category_major = ind.national_standard_industry_category_major
            company.qichacha_industry_category_main = ind.qcc_industry_category_main
            company.qichacha_industry_category_major = ind.qcc_industry_category_major
        
        # Tech
        tech = db.query(models.QCCTech).filter_by(company_name=company.company_name).first()
        if tech:
            company.is_little_giant_enterprise = tech.is_little_giant_enterprise
            company.is_srun_sme = tech.is_srun_sme
            company.is_high_tech_enterprise = tech.is_high_tech_enterprise
            company.is_innovative_sme = tech.is_innovative_sme
            company.is_tech_based_sme = tech.is_tech_based_sme
        
        # QYJH
        qyjh_item = db.query(models.QYJHList).filter_by(company_name=company.company_name).first()
        company.qyjh_category = qyjh_item.qyjh_category if qyjh_item else None
        
        # Derived Technology Flag
        company.is_technology_enterprise = any([
            company.is_little_giant_enterprise, company.is_srun_sme,
            company.is_high_tech_enterprise, company.is_innovative_sme,
            company.is_tech_based_sme, pd.notna(company.qyjh_category)
        ])
        count += 1
    
    db.commit()
    return count

def read_data(file, db: Session):
    xl = pd.ExcelFile(file)
    
    data_1 = read_sheet_data(xl, "线下业务", 1,
                             ["企业名称", "借款金额（万元）", "担保金额（万元）", "借款起始日", "借款到期日", "借款利率",
                              "担保费率", "借款余额（万元）", "担保余额（万元）", "借据状态", "结清日期", "企业划型",
                              "合作银行", "业务年度"], "常规业务")
    
    data_2 = read_sheet_data(xl, "微众批量业务", 1,
                             ["企业名称", "借款金额（万元）", "借款起始日", "借款到期日", "借款利率", "担保费率",
                              "借款余额（万元）", "担保余额（万元）", "借据状态", "结清日期", "企业划型"], "微众批量业务",
                             "微众银行")
    
    data_3 = read_sheet_data(xl, "建行批量业务", 1,
                             ["企业名称", "借款金额（万元）", "担保金额（万元）", "借款起始日", "借款到期日", "借款利率",
                              "担保费率", "借款余额（万元）", "担保余额（万元）", "借据状态", "结清日期", "企业划型",
                              "业务年度"], "建行批量业务", "建设银行")
    
    data_4 = read_sheet_data(xl, "工行批量业务", 1,
                             ["企业名称", "借款金额（万元）", "担保金额（万元）", "借款起始日", "借款到期日", "借款利率",
                              "担保费率", "借款余额（万元）", "担保余额（万元）", "借据状态", "结清日期", "企业划型",
                              "业务年度"], "工行批量业务", "工商银行")

    if not data_2.empty:
        if '借款起始日' in data_2.columns:
            data_2['借款起始日'] = pd.to_datetime(data_2['借款起始日'], errors='coerce')
            data_2["业务年度"] = data_2["借款起始日"].dt.year
        if '借款金额（万元）' in data_2.columns:
            data_2["担保金额（万元）"] = data_2["借款金额（万元）"].apply(
                lambda x: (Decimal(str(x)) * Decimal('0.8')) if pd.notna(x) else Decimal('0')
            )

    result_total = pd.concat([data_1, data_2, data_3, data_4], ignore_index=True)
    result_total.dropna(subset=["企业名称"], inplace=True)
    
    junk_keywords = ["/", "合计", "总计", "TOTAL", "nan", "None", "企业名称"]
    result_total = result_total[~result_total['企业名称'].astype(str).str.contains('|'.join(junk_keywords), case=False)]
    result_total = result_total[result_total['企业名称'].astype(str).str.len() >= 2]
    
    if '业务年度' in result_total.columns:
        result_total["业务年度"] = pd.to_numeric(result_total["业务年度"], errors='coerce').fillna(0).astype(int)
    if '企业划型' in result_total.columns:
        result_total["企业划型"] = result_total["企业划型"].replace({"微型企业": "微型", "小微企业": "小型", "小型企业": "小型", "中型企业": "中型", "大型企业": "大型"})
    if '借据状态' in result_total.columns:
        result_total["借据状态"] = result_total["借据状态"].replace({"是": "已结清", "否": "正常"})

    numeric_cols = ["借款金额（万元）", "担保金额（万元）", "借款余额（万元）", "担保余额（万元）", "借款利率", "担保费率"]
    for col in numeric_cols:
        if col in result_total.columns:
            result_total[col] = pd.to_numeric(result_total[col], errors='coerce').fillna(0)

    raw_data = merge_qcc_data(result_total, db)
    return raw_data

def process_excel_import(db: Session, file_contents: bytes, schema_type: str, year: int = None, month: int = None):
    now = datetime.datetime.now()
    if year is None: year = now.year
    if month is None: month = now.month

    if schema_type == 'business_data':
        file_obj = io.BytesIO(file_contents)
        processed_data = read_data(file_obj, db)
        
        crud.delete_business_data_by_snapshot(db, year, month)

        data_to_insert = []
        for _, row in processed_data.iterrows():
            name = row['企业名称']
            company = get_or_create_company(db, name)
            
            # Update company attributes from latest import
            company.enterprise_size = row.get('企业规模')
            company.enterprise_institution_type = row.get('企业（机构）类型')
            company.national_standard_industry_category_main = row.get('国标行业门类')
            company.national_standard_industry_category_major = row.get('国标行业大类')
            company.qichacha_industry_category_main = row.get('企查查行业门类')
            company.qichacha_industry_category_major = row.get('企查查行业大类')
            company.is_little_giant_enterprise = row.get('专精特新“小巨人”企业') == '是'
            company.is_srun_sme = row.get('专精特新中小企业') == '是'
            company.is_high_tech_enterprise = row.get('高新技术企业') == '是'
            company.is_innovative_sme = row.get('创新型中小企业') == '是'
            company.is_tech_based_sme = row.get('科技型中小企业') == '是'
            company.is_technology_enterprise = row.get('科技企业') == '是'
            company.qyjh_category = row.get('千亿计划') if pd.notna(row.get('千亿计划')) and row.get('千亿计划') != '否' else None

            loan_start = pd.to_datetime(row.get('借款起始日')).date() if pd.notna(row.get('借款起始日')) else None
            
            def to_decimal(val):
                try: return Decimal(str(val)) if pd.notna(val) and str(val).strip() != "" else Decimal('0')
                except: return Decimal('0')

            record = {
                'company_id': company.id,
                'loan_amount': to_decimal(row.get('借款金额（万元）')),
                'guarantee_amount': to_decimal(row.get('担保金额（万元）')),
                'loan_start_date': loan_start,
                'loan_due_date': pd.to_datetime(row.get('借款到期日')).date() if pd.notna(row.get('借款到期日')) else None,
                'loan_interest_rate': to_decimal(row.get('借款利率')),
                'guarantee_fee_rate': to_decimal(row.get('担保费率')),
                'outstanding_loan_balance': to_decimal(row.get('借款余额（万元）')),
                'outstanding_guarantee_balance': to_decimal(row.get('担保余额（万元）')),
                'loan_status': row.get('借据状态'),
                'settlement_date': pd.to_datetime(row.get('结清日期')).date() if pd.notna(row.get('结清日期')) else None,
                'enterprise_classification': row.get('企业划型'),
                'cooperative_bank': row.get('合作银行'),
                'snapshot_year': year,
                'snapshot_month': month,
                'business_year': int(row['业务年度']) if pd.notna(row['业务年度']) and row['业务年度'] != 0 else (loan_start.year if loan_start else year),
                'business_type': row.get('业务类型')
            }
            data_to_insert.append(record)

        db.bulk_insert_mappings(models.BusinessData, data_to_insert)
        db.commit()
        return len(data_to_insert)

    # Master data imports (Industry/Tech/QYJH) remain similar but should update models.Company if applicable
    # (Leaving them mostly as is for now as they are staging tables in this demo)
    return 0

def delete_data(db: Session, snapshot_year: int, snapshot_month: int):
    crud.delete_business_data_by_snapshot(db, snapshot_year, snapshot_month)

def get_statistics(db: Session, year, month):
    target_year, target_month = int(year), int(month)
    
    # Query with JOIN
    query = db.query(models.BusinessData).join(models.Company).filter(
        or_(
            (models.BusinessData.snapshot_year < target_year) & (models.BusinessData.snapshot_month == 12),
            (models.BusinessData.snapshot_year == target_year) & (models.BusinessData.snapshot_month == target_month)
        )
    )
    
    records = query.all()
    if not records: return {}

    # Flatten joined results into a list of dicts for Pandas
    data = []
    for r in records:
        d = r.__dict__.copy()
        d.pop('_sa_instance_state', None)
        d['company_name'] = r.company.company_name # Essential for unique counts
        data.append(d)
        
    df = pd.DataFrame(data)
    df = df[~(df['loan_status'] == '未放款')]
    if df.empty: return {}

    for col in ['loan_amount', 'guarantee_amount', 'outstanding_loan_balance', 'outstanding_guarantee_balance']:
        df[col] = df[col].apply(lambda x: Decimal(str(x)) if pd.notna(x) else Decimal('0'))

    business_types = ['常规业务', '建行批量业务', '微众批量业务', '工行批量业务']

    def calculate_summary(year_df, full_df):
        summary = {}
        sum_company_count = 0
        sum_cumulative_company_count = 0
        sum_in_force_companies_count = 0

        for b_type in business_types:
            type_df = year_df[year_df['business_type'] == b_type]
            type_full_df = full_df[full_df['business_type'] == b_type]
            
            c_count = int(type_df[type_df['guarantee_amount'] > 0]['company_name'].nunique())
            cum_c_count = int(type_full_df[type_full_df['guarantee_amount'] > 0]['company_name'].nunique())
            inf_c_count = int(type_full_df[type_full_df['outstanding_guarantee_balance'] > 0]['company_name'].nunique())

            summary[b_type] = {
                'loan_amount': float(type_df['loan_amount'].sum()),
                'guarantee_amount': float(type_df['guarantee_amount'].sum()),
                'company_count': c_count,
                'cumulative_company_count': cum_c_count,
                'in_force_companies_count': inf_c_count,
                'loan_balance': float(type_full_df['outstanding_loan_balance'].sum()),
                'guarantee_balance': float(type_full_df['outstanding_guarantee_balance'].sum()),
            }
            sum_company_count += c_count
            sum_cumulative_company_count += cum_c_count
            sum_in_force_companies_count += inf_c_count

        total_df = year_df[year_df['business_type'].isin(business_types)]
        total_full_df = full_df[full_df['business_type'].isin(business_types)]
        
        summary['合计'] = {
            'loan_amount': float(total_df['loan_amount'].sum()),
            'guarantee_amount': float(total_df['guarantee_amount'].sum()),
            'company_count': sum_company_count,
            'cumulative_company_count': sum_cumulative_company_count,
            'in_force_companies_count': sum_in_force_companies_count,
            'loan_balance': float(total_full_df['outstanding_loan_balance'].sum()),
            'guarantee_balance': float(total_full_df['outstanding_guarantee_balance'].sum()),
        }
        summary['merged_unique_company'] = int(total_df[total_df['guarantee_amount'] > 0]['company_name'].nunique())
        summary['merged_cumlative_unique_company'] = int(total_full_df[total_full_df['guarantee_amount'] > 0]['company_name'].nunique())
        summary['merged_unique_company_count_in_force'] = int(total_full_df[total_full_df['outstanding_guarantee_balance'] > 0]['company_name'].nunique())
        return summary

    df_overall = df[(df['snapshot_year'] == target_year) & (df['snapshot_month'] == target_month)]
    overall_summary = calculate_summary(df_overall, df_overall)
    
    yearly_summaries = {}
    for y in range(2021, target_year + 1):
        df_snapshot = df[(df['snapshot_year'] == y) & (df['snapshot_month'] == 12)] if y < target_year else df_overall
        if not df_snapshot.empty:
            df_year = df_snapshot[df_snapshot['business_year'] == y]
            yearly_summaries[str(int(y))] = calculate_summary(df_year, df_snapshot)
        
    return {"overall_summary": overall_summary, "yearly_summaries": yearly_summaries}

def get_data_status(db: Session, year, month, limit=None):
    query = db.query(models.BusinessData).join(models.Company).filter(
        models.BusinessData.snapshot_year == year,
        models.BusinessData.snapshot_month == month
    )
    if limit: query = query.limit(limit)
    
    result = query.all()
    data = []
    for r in result:
        item = {col.name: getattr(r, col.name) for col in r.__table__.columns}
        # Add company attributes
        for col in r.company.__table__.columns:
            item[f"company_{col.name}"] = getattr(r.company, col.name)
        
        for key, value in item.items():
            if isinstance(value, (datetime.date, datetime.datetime)): item[key] = value.isoformat()
            elif isinstance(value, Decimal): item[key] = float(value)
        data.append(item)
    return data

def export_data_status_to_excel(db: Session, year, month):
    data = get_data_status(db, year, month)
    if not data: raise ValueError("No data found")
    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Data Status')
    output.seek(0)
    return output
