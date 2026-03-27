/**
 * 业务数据统计渲染与导出逻辑
 */

// 全局变量，存储当前数据
let statisticsData = null;
let currentYear = null;
let currentMonth = null;

const businessTypes = ['常规业务', '建行批量业务', '微众批量业务', '工行批量业务', '合计'];
const columns = [
    '新增借款金额（万元）',
    '新增担保金额（万元）',
    '新增担保企业数量（家）',
    '累计担保企业数量（家）',
    '在保企业（家）',
    '借款余额（万元）',
    '担保余额（万元）',
];

/**
 * 从后端获取统计数据
 */
async function fetchStatistics(year, month) {
    if (!year || !month) return;
    
    currentYear = year;
    currentMonth = month;
    
    const container = document.getElementById('statisticsContainer');
    if (container) {
        container.innerHTML = '<div class="text-center my-4"><div class="spinner-border text-primary" role="status"></div><p>正在加载统计数据...</p></div>';
    }

    try {
        const response = await fetch(`/statistics/?snapshot_year=${year}&snapshot_month=${month}`);
        if (!response.ok) throw new Error('获取统计数据失败');
        
        statisticsData = await response.json();
        renderStatistics();
    } catch (error) {
        console.error('获取统计数据时出错:', error);
        if (container) {
            container.innerHTML = `<div class="alert alert-danger">错误: ${error.message}</div>`;
        }
    }
}

/**
 * 将统计表格渲染到 DOM 中
 */
function renderStatistics() {
    const container = document.getElementById('statisticsContainer');
    if (!container) return;

    if (!statisticsData || Object.keys(statisticsData).length === 0) {
        container.innerHTML = '<div class="alert alert-info">该时段没有可用的统计数据。</div>';
        return;
    }

    let html = `
        <div class="d-flex justify-content-between align-items-center my-4">
            <h2>业务数据统计 - ${currentYear}年${currentMonth}月</h2>
            <button class="btn btn-success" onclick="handleExportToExcel()">导出到 Excel</button>
        </div>
    `;

    // 总体统计 (Cumulative)
    if (statisticsData.overall_summary) {
        html += renderTable(`2021年10月至${currentYear}年${currentMonth}月`, statisticsData.overall_summary);
    }

    // 年度统计 (Yearly Summaries)
    if (statisticsData.yearly_summaries) {
        // 使用 yearA, yearB 作为通用参数进行排序
        const years = Object.keys(statisticsData.yearly_summaries).sort((yearA, yearB) => parseInt(yearB) - parseInt(yearA));
        years.forEach(year => {
            html += renderTable(`${year}全年统计`, statisticsData.yearly_summaries[year]);
        });
    }

    container.innerHTML = html;
}

/**
 * 生成单个统计表格的 HTML
 */
function renderTable(title, data) {
    let rowsHtml = '';
    
    businessTypes.forEach(type => {
        const item = data[type] || {};
        rowsHtml += `
            <tr>
                <td>${type}</td>
                <td>${formatNumber(item.loan_amount)}</td>
                <td>${formatNumber(item.guarantee_amount)}</td>
                <td>${item.company_count || 0}</td>
                <td>${item.cumulative_company_count || 0}</td>
                <td>${item.in_force_companies_count || 0}</td>
                <td>${formatNumber(item.loan_balance)}</td>
                <td>${formatNumber(item.guarantee_balance)}</td>
            </tr>
        `;
    });

    // 合并去重行
    rowsHtml += `
        <tr class="table-info">
            <td>合并去重数</td>
            <td></td>
            <td></td>
            <td>${data.merged_unique_company || 0}</td>
            <td>${data.merged_cumlative_unique_company || 0}</td>
            <td>${data.merged_unique_company_count_in_force || 0}</td>
            <td></td>
            <td></td>
        </tr>
    `;

    return `
        <div class="card mb-4 shadow-sm">
            <div class="card-header bg-primary text-white">
                <h5 class="mb-0">${title}</h5>
            </div>
            <div class="card-body p-0">
                <div class="table-responsive">
                    <table class="table table-striped table-bordered table-hover mb-0 text-center">
                        <thead class="table-light">
                            <tr>
                                <th>业务类型</th>
                                ${columns.map(col => `<th>${col}</th>`).join('')}
                            </tr>
                        </thead>
                        <tbody>
                            ${rowsHtml}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    `;
}

function formatNumber(value) {
    return typeof value === 'number' ? value.toFixed(2) : '0.00';
}

/**
 * 导出到 Excel 功能
 */
function handleExportToExcel() {
    if (!statisticsData || !window.XLSX) {
        alert('XLSX 库未加载或没有可导出的数据。');
        return;
    }

    const allData = [];

    const processDataForSheet = (title, data) => {
        allData.push([title]);
        allData.push(['业务类型', ...columns]);

        businessTypes.forEach(type => {
            const item = data[type] || {};
            const row = [
                type,
                item.loan_amount || 0,
                item.guarantee_amount || 0,
                item.company_count || 0,
                item.cumulative_company_count || 0,
                item.in_force_companies_count || 0,
                item.loan_balance || 0,
                item.guarantee_balance || 0
            ];
            allData.push(row);
        });

        allData.push([
            '合并去重数',
            '',
            '',
            data.merged_unique_company || 0,
            data.merged_cumlative_unique_company || 0,
            data.merged_unique_company_count_in_force || 0,
            '',
            ''
        ]);
        allData.push([]); // 空行
    };

    if (statisticsData.overall_summary) {
        processDataForSheet(`2021年10月至${currentYear}年${currentMonth}月`, statisticsData.overall_summary);
    }

    if (statisticsData.yearly_summaries) {
        const years = Object.keys(statisticsData.yearly_summaries).sort((a, b) => b - a);
        years.forEach(year => {
            processDataForSheet(`${year}全年统计`, statisticsData.yearly_summaries[year]);
        });
    }

    const wb = XLSX.utils.book_new();
    const ws = XLSX.utils.aoa_to_sheet(allData);
    XLSX.utils.book_append_sheet(wb, ws, "业务数据统计");
    XLSX.writeFile(wb, `业务数据统计_${currentYear}_${currentMonth}.xlsx`);
}
