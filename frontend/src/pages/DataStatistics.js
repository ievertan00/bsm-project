import React, { useState, useEffect, useContext } from 'react';
import axios from 'axios';
import { Card, Col, Row, Table } from 'react-bootstrap';
import { DataContext } from '../DataContext';
import DateSelector from '../components/DateSelector';

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
            axios.get(`/api/statistics?year=${selectedYear}&month=${selectedMonth}`)
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
        '借款金额（万元）',
        '担保金额（万元）',
        '借款企业数量（家）',
        '累计借款企业数量（家）',
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
                            <td>{dataToRender.merged_unique_company_count_loan}</td>
                            <td>{dataToRender.merged_unique_company_count_cumulative_loan}</td>
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

            {statisticsData.overall_summary && renderTable(`总览统计 (${selectedYear}年${selectedMonth}月)`, statisticsData.overall_summary)}

            {Object.keys(statisticsData.yearly_summaries).sort().map(year => (
                renderTable(`${year}年统计`, statisticsData.yearly_summaries[year])
            ))}
        </div>
    );
}

export default DataStatistics;