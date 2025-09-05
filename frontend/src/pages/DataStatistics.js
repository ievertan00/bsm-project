import React, { useState, useEffect, useContext } from 'react';
import { Card, Col, Row, Table, Button } from 'react-bootstrap';
import api from '../api';
import { DataContext } from '../DataContext';
import DateSelector from '../components/DateSelector';
import * as XLSX from 'xlsx';

function DataStatistics() {
    const { availableYears, availableMonths } = useContext(DataContext);
    const [selectedYear, setSelectedYear] = useState(null);
    const [selectedMonth, setSelectedMonth] = useState(null);
    const [statisticsData, setStatisticsData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        if (availableYears && availableYears.length > 0) {
            const latestYear = Math.max(...availableYears);
            setSelectedYear(latestYear);

            const monthsForLatestYear = availableMonths
                .filter(m => m.year === latestYear)
                .map(m => m.month);

            if (monthsForLatestYear.length > 0) {
                const latestMonth = Math.max(...monthsForLatestYear);
                setSelectedMonth(latestMonth);
            }
        }
    }, [availableYears, availableMonths]);

    useEffect(() => {
        if (selectedYear && selectedMonth) {
            setLoading(true);
            setError('');
            api.get(`/api/statistics?year=${selectedYear}&month=${selectedMonth}`)
                .then(response => {
                    setStatisticsData(response.data);
                    setLoading(false);
                })
                .catch(err => {
                    console.error("获取统计数据时出错:", err);
                    setError("无法加载统计数据。");
                    setLoading(false);
                    setStatisticsData(null); // Clear data on error
                });
        }
    }, [selectedYear, selectedMonth]);

    const handleYearChange = (e) => {
        const year = parseInt(e.target.value);
        setSelectedYear(year);
        const monthsForNewYear = availableMonths.filter(m => m.year === year).map(m => m.month);
        if (monthsForNewYear.length > 0) {
            setSelectedMonth(Math.max(...monthsForNewYear));
        }
    };

    const handleMonthChange = (e) => {
        setSelectedMonth(parseInt(e.target.value));
    };

    const formatNumber = (value) => {
        return typeof value === 'number' ? value.toFixed(2) : 'N/A';
    };

    

    const handleExportToExcel = () => {
        if (!statisticsData) return;

        const allData = [];
        const rowMetadata = []; // To track row types for styling

        const processDataForSheet = (title, data) => {
            // Add title
            allData.push([title]);
            rowMetadata.push({ type: 'title' });

            // Add header
            const header = ['业务类型', ...columns];
            allData.push(header);
            rowMetadata.push({ type: 'header' });

            // Add data rows
            businessTypes.forEach(type => {
                const row = [type];
                row.push(typeof data[type]?.loan_amount === 'number' ? data[type]?.loan_amount.toFixed(2) : 'N/A');
                row.push(typeof data[type]?.guarantee_amount === 'number' ? data[type]?.guarantee_amount.toFixed(2) : 'N/A');
                row.push(data[type]?.company_count);
                row.push(data[type]?.cumulative_company_count);
                row.push(data[type]?.in_force_companies_count);
                row.push(typeof data[type]?.loan_balance === 'number' ? data[type]?.loan_balance.toFixed(2) : 'N/A');
                row.push(typeof data[type]?.guarantee_balance === 'number' ? data[type]?.guarantee_balance.toFixed(2) : 'N/A');
                allData.push(row);
                rowMetadata.push({ type: 'data' });
            });

            // Add merged data row
            const mergedRow = [
                '合并去重数',
                '',
                '',
                data.merged_unique_company,
                data.merged_cumlative_unique_company,
                data.merged_unique_company_count_in_force,
                '',
                ''
            ];
            allData.push(mergedRow);
            rowMetadata.push({ type: 'data' });

            // Add a blank row for spacing
            allData.push([]);
            rowMetadata.push({ type: 'spacer' });
        };

        // Overall Summary
        if (statisticsData.overall_summary) {
            processDataForSheet(`2021年10月至${selectedYear}年${selectedMonth}月`, statisticsData.overall_summary);
        }

        // Yearly Summaries
        Object.keys(statisticsData.yearly_summaries)
            .sort((yearA, yearB) => parseInt(yearB) - parseInt(yearA))
            .forEach(year => {
                processDataForSheet(`${year}全年统计`, statisticsData.yearly_summaries[year]);
            });

        const wb = XLSX.utils.book_new();
        const ws = XLSX.utils.aoa_to_sheet(allData);

        const colWidths = allData[1].map(() => ({ wch: 25 }));

        ws['!cols'] = colWidths;

        XLSX.utils.book_append_sheet(wb, ws, '业务数据统计');
        XLSX.writeFile(wb, `业务数据统计-${selectedYear}年${selectedMonth}月.xlsx`);
    };

    if (loading) {
        return <div>正在加载数据统计...</div>;
    }

    if (error) {
        return <div className="alert alert-danger">{error}</div>;
    }

    if (!statisticsData || Object.keys(statisticsData).length === 0) {
        return <div className="alert alert-info">没有可用的统计数据。</div>;
    }

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

    const renderTable = (title, dataToRender) => (
        <Card className="mb-4">
            <Card.Header><h3>{title}</h3></Card.Header>
            <Card.Body>
                <Table striped bordered hover responsive className="text-center">
                    <thead>
                        <tr>
                            <th>业务类型</th>
                            {columns.map(col => <th key={col}>{col}</th>)}
                        </tr>
                    </thead>
                    <tbody>
                        {businessTypes.map(type => (
                            <tr key={type}>
                                <td>{type}</td>
                                <td>{formatNumber(dataToRender[type]?.loan_amount)}</td>
                                <td>{formatNumber(dataToRender[type]?.guarantee_amount)}</td>
                                <td>{dataToRender[type]?.company_count}</td>
                                <td>{dataToRender[type]?.cumulative_company_count}</td>
                                <td>{dataToRender[type]?.in_force_companies_count}</td>
                                <td>{formatNumber(dataToRender[type]?.loan_balance)}</td>
                                <td>{formatNumber(dataToRender[type]?.guarantee_balance)}</td>
                            </tr>
                        ))}
                        <tr>
                            <td>合并去重数</td>
                            <td></td>
                            <td></td>
                            <td>{dataToRender.merged_unique_company}</td>
                            <td>{dataToRender.merged_cumlative_unique_company}</td>
                            <td>{dataToRender.merged_unique_company_count_in_force}</td>
                            <td></td>
                            <td></td>
                        </tr>
                    </tbody>
                </Table>
            </Card.Body>
        </Card>
    );

    return (
        <div className="container-fluid">
            <h2 className="my-4">业务数据统计 - {selectedYear}年{selectedMonth}月</h2>
            <DateSelector 
                selectedYear={selectedYear}
                selectedMonth={selectedMonth}
                availableYears={availableYears}
                availableMonths={availableMonths}
                onYearChange={handleYearChange}
                onMonthChange={handleMonthChange}
            />

            <Button variant="primary" onClick={handleExportToExcel} className="mb-3">
                导出到 Excel
            </Button>

            {statisticsData.overall_summary && renderTable(`2021年10月至${selectedYear}年${selectedMonth}月`, statisticsData.overall_summary)}

            {Object.keys(statisticsData.yearly_summaries)
                .sort((yearA, yearB) => parseInt(yearB) - parseInt(yearA)) // Using yearA and yearB as generic parameters
                .map(year => (
                    renderTable(`${year}全年统计`, statisticsData.yearly_summaries[year])
                ))}
        </div>
    );
}

export default DataStatistics;