import pandas as pd

# 读取文件
excel_file = pd.ExcelFile('sample_data_2025_5.xlsx')

# 获取指定工作表中的数据
df = excel_file.parse('2025-5月汇总')

# 转换借款起始日列的数据类型为日期类型，无法转换的值会变为NaT
df['借款起始日'] = pd.to_datetime(df['借款起始日'], errors='coerce')

# 遍历2021_10至2025_4的每个时间段
for year in range(2021, 2026):
    start_month = 10 if year == 2021 else 1
    end_month = 4 if year == 2025 else 12
    for month in range(start_month, end_month + 1):
        # 生成文件名中的日期字符串
        date_str = f'{year}-{month}'

        # 创建当前月份的日期对象
        current_date = pd.to_datetime(f'{year}-{month}-01')

        # 筛选借款起始日小于等于当前日期的数据，或借款起始日为0/空值的数据
        condition = (df['借款起始日'] <= current_date)
        filtered_df = df[condition].copy()  # 创建副本，避免SettingWithCopyWarning
        filtered_df['借款余额（万元）'] = filtered_df['借款金额（万元）']
        filtered_df['担保余额（万元）'] = filtered_df['担保金额（万元）']


        # 在保存文件前，将筛选后数据中借款起始日小于2020年的记录修改为0
        filtered_df.loc[filtered_df['借款起始日'] < '2020-01-01', '借款起始日'] = 0

        # 保存筛选并修改后的数据到新的 Excel 文件
        file_path = f'sample_data_{date_str}.xlsx'
        filtered_df.to_excel(file_path, index=False)