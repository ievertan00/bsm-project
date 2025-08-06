import React, { useState, useEffect, useContext } from 'react';
import axios from 'axios';
import { Card, Col, Row } from 'react-bootstrap';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line } from 'recharts';
import { DataContext } from '../../DataContext';

const businessTypeColors = {
    '常规业务': '#FAC795',
    '建行批量业务': '#FFE9BE',
    '微众批量业务': '#E3EDE0',
    '工行批量业务': '#ABD3E1',
    '整体': '#C59D94'
};

const yearlyColors = ['#FAC795', '#FFE9BE', '#E3EDE0', '#ABD3E1', '#C59D94'];


const BusinessProportionCharts = ({ chartData }) => {
    if (!chartData || !chartData.money_results || !chartData.num_results || !chartData.grand_total_loan_amount || !chartData.grand_total_companies) {
        return null;
    }

    const { money_results, num_results, grand_total_loan_amount, grand_total_companies } = chartData;
    const business_types = ['常规业务', '建行批量业务', '微众批量业务', '工行批量业务'];

    const numData = business_types.map(type => ({
        name: type,
        value: num_results.total[type] || 0
    }));

    const moneyData = business_types.map(type => ({
        name: type,
        value: money_results.total[type] || 0
    }));

    const RADIAN = Math.PI / 180;
    const renderCustomizedLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percent, index }) => {
        const radius = innerRadius + (outerRadius - innerRadius) * 0.5;
        const x = cx + radius * Math.cos(-midAngle * RADIAN);
        const y = cy + radius * Math.sin(-midAngle * RADIAN);

        return (
            <text x={x} y={y} fill="black" textAnchor={x > cx ? 'start' : 'end'} dominantBaseline="central">
                {`${(percent * 100).toFixed(1)}%`}
            </text>
        );
    };

    const text_pct = `微众批量业务数量占比${grand_total_companies > 0 ? (num_results.total['微众批量业务'] / grand_total_companies).toLocaleString(undefined, { style: 'percent', minimumFractionDigits: 2 }) : '0.00%'}, 金额占比${grand_total_loan_amount > 0 ? (money_results.total['微众批量业务'] / grand_total_loan_amount).toLocaleString(undefined, { style: 'percent', minimumFractionDigits: 2 }) : '0.00%'}; 常规业务数量占比${grand_total_companies > 0 ? (num_results.total['常规业务'] / grand_total_companies).toLocaleString(undefined, { style: 'percent', minimumFractionDigits: 2 }) : '0.00%'}, 金额占比${grand_total_loan_amount > 0 ? (money_results.total['常规业务'] / grand_total_loan_amount).toLocaleString(undefined, { style: 'percent', minimumFractionDigits: 2 }) : '0.00%'}; 建行批量业务数量占比${grand_total_companies > 0 ? (num_results.total['建行批量业务'] / grand_total_companies).toLocaleString(undefined, { style: 'percent', minimumFractionDigits: 2 }) : '0.00%'}, 金额占比${grand_total_loan_amount > 0 ? (money_results.total['建行批量业务'] / grand_total_loan_amount).toLocaleString(undefined, { style: 'percent', minimumFractionDigits: 2 }) : '0.00%'}; 工行批量业务数量占比${grand_total_companies > 0 ? (num_results.total['工行批量业务'] / grand_total_companies).toLocaleString(undefined, { style: 'percent', minimumFractionDigits: 2 }) : '0.00%'}, 金额占比${grand_total_loan_amount > 0 ? (money_results.total['工行批量业务'] / grand_total_loan_amount).toLocaleString(undefined, { style: 'percent', minimumFractionDigits: 2 }) : '0.00%'}。`;


    return (
        <Card className="mt-4">
            <Card.Header>
                <h4>业务占比情况</h4>
            </Card.Header>
            <Card.Body>
                <Row>
                    <Col md={6}>
                        <h5 className="text-center">企业家数</h5>
                        <ResponsiveContainer width="100%" height={300}>
                            <PieChart>
                                <Pie
                                    data={numData}
                                    cx="50%"
                                    cy="50%"
                                    labelLine={false}
                                    label={renderCustomizedLabel}
                                    outerRadius={80}
                                    innerRadius={40}
                                    fill="#8884d8"
                                    dataKey="value"
                                >
                                    {numData.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={businessTypeColors[entry.name]} />
                                    ))}
                                </Pie>
                                <Tooltip formatter={(value) => `${value} 家`} />
                                <Legend />
                            </PieChart>
                        </ResponsiveContainer>
                    </Col>
                    <Col md={6}>
                        <h5 className="text-center">借款金额</h5>
                        <ResponsiveContainer width="100%" height={300}>
                            <PieChart>
                                <Pie
                                    data={moneyData}
                                    cx="50%"
                                    cy="50%"
                                    labelLine={false}
                                    label={renderCustomizedLabel}
                                    outerRadius={80}
                                    innerRadius={40}
                                    fill="#8884d8"
                                    dataKey="value"
                                >
                                    {moneyData.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={businessTypeColors[entry.name]} />
                                    ))}
                                </Pie>
                                <Tooltip formatter={(value) => `${value.toLocaleString()} 万元`} />
                                <Legend />
                            </PieChart>
                        </ResponsiveContainer>
                    </Col>
                </Row>
                <p className="mt-3">{text_pct}</p>
            </Card.Body>
        </Card>
    );
};

const AverageAmountChart = ({ avgAmountData }) => {
    if (!avgAmountData) return null;

    const { by_type, overall } = avgAmountData;
    const business_types = ['常规业务', '建行批量业务', '微众批量业务', '工行批量业务', '整体'];

    const chartData = business_types.map(bt => ({
        name: bt,
        '平均借款金额': (bt === '整体' ? overall.avg_loan_amount : by_type[bt]?.avg_loan_amount) || 0,
        '平均担保金额': (bt === '整体' ? overall.avg_guarantee_amount : by_type[bt]?.avg_guarantee_amount) || 0,
    }));

    const formatValue = (value) => value ? value.toFixed(2) : '0.00';

    const text_max_min = `常规业务最高金额${formatValue(by_type['常规业务']?.max_loan_amount)}万元，最低${formatValue(by_type['常规业务']?.min_loan_amount)}万元；建行业务最高金额${formatValue(by_type['建行批量业务']?.max_loan_amount)}万元，最低${formatValue(by_type['建行批量业务']?.min_loan_amount)}万元；微众业务最高金额${formatValue(by_type['微众批量业务']?.max_loan_amount)}万元，最低${formatValue(by_type['微众批量业务']?.min_loan_amount)}万元；工行业务最高${formatValue(by_type['工行批量业务']?.max_loan_amount)}万元，最低${formatValue(by_type['工行批量业务']?.min_loan_amount)}万元。`;
    const text_avg = `常规业务平均借款金额${formatValue(by_type['常规业务']?.avg_loan_amount)}万元，平均担保金额${formatValue(by_type['常规业务']?.avg_guarantee_amount)}万元；建行业务平均借款金额${formatValue(by_type['建行批量业务']?.avg_loan_amount)}万元，平均担保金额${formatValue(by_type['建行批量业务']?.avg_guarantee_amount)}万元；微众业务平均借款金额${formatValue(by_type['微众批量业务']?.avg_loan_amount)}万元，平均担保金额${formatValue(by_type['微众批量业务']?.avg_guarantee_amount)}万元；工行业务平均借款金额${formatValue(by_type['工行批量业务']?.avg_loan_amount)}万元，平均担保金额${formatValue(by_type['工行批量业务']?.avg_guarantee_amount)}万元；整体业务平均借款金额${formatValue(overall.avg_loan_amount)}万元，平均担保金额${formatValue(overall.avg_guarantee_amount)}万元。`;

    return (
        <Card className="mt-4">
            <Card.Header>
                <h4>平均借款金额及担保金额</h4>
            </Card.Header>
            <Card.Body>
                <ResponsiveContainer width="100%" height={400}>
                    <BarChart data={chartData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="name" />
                        <YAxis />
                        <Tooltip formatter={(value) => `${value.toLocaleString()} 万元`} />
                        <Legend />
                        <Bar dataKey="平均借款金额" fill={yearlyColors[0]} />
                        <Bar dataKey="平均担保金额" fill={yearlyColors[1]} />
                    </BarChart>
                </ResponsiveContainer>
                <p className="mt-3">{text_max_min}</p>
                <p>{text_avg}</p>
            </Card.Body>
        </Card>
    );
};

const DueDateChart = ({ dueDateData }) => {
    if (!dueDateData) return null;

    const years = ['2024', '2025', '2026'];
    const monthNames = ['一月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月', '十月', '十一月', '十二月'];

    return (
        <Card className="mt-4">
            <Card.Header>
                <h4>业务到期情况统计</h4>
            </Card.Header>
            <Card.Body>
                {years.map(year => (
                    <div key={year}>
                        <h5>{year}年</h5>
                        <ResponsiveContainer width="100%" height={300}>
                            <BarChart data={dueDateData[year]} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="due_month" tickFormatter={(tick) => monthNames[tick - 1]} />
                                <YAxis />
                                <Tooltip formatter={(value) => `${value.toLocaleString()} 万元`} />
                                <Legend />
                                <Bar dataKey="non_weizhong_amount" stackId="a" name="非微众业务" fill='#ABD3E1' />
                                <Bar dataKey="weizhong_amount" stackId="a" name="微众批量业务" fill='#FFE9BE' />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                ))}
            </Card.Body>
        </Card>
    );
};

const BalanceProjectionChart = ({ projectionData }) => {
    if (!projectionData) return null;

    return (
        <Card className="mt-4">
            <Card.Header>
                <h4>余额变动情况</h4>
            </Card.Header>
            <Card.Body>
                <ResponsiveContainer width="100%" height={400}>
                    <LineChart data={projectionData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="date" />
                        <YAxis />
                        <Tooltip formatter={(value) => `${value.toLocaleString()} 万元`} />
                        <Legend />
                        <Line type="monotone" dataKey="loan_balance" name="借款余额" stroke="#DBDB8D" />
                        <Line type="monotone" dataKey="guarantee_balance" name="担保余额" stroke="#F09148" />
                    </LineChart>
                </ResponsiveContainer>
            </Card.Body>
        </Card>
    );
};


function ChartsDisplay() {
    const { selectedYear, selectedMonth } = useContext(DataContext);
    const [chartData, setChartData] = useState(null);
    const [avgAmountData, setAvgAmountData] = useState(null);
    const [dueDateData, setDueDateData] = useState(null);
    const [projectionData, setProjectionData] = useState(null);

    useEffect(() => {
        if (selectedYear && selectedMonth) {
            const chartsDataPromise = axios.get(`/api/charts-data?year=${selectedYear}&month=${selectedMonth}`);
            const avgAmountsPromise = axios.get(`/api/analysis/average_amounts?year=${selectedYear}&month=${selectedMonth}`);
            const dueDatePromise = axios.get(`/api/analysis/due_date_summary?year=${selectedYear}&month=${selectedMonth}`);
            const projectionPromise = axios.get(`/api/analysis/balance_projection?year=${selectedYear}&month=${selectedMonth}`);

            Promise.all([chartsDataPromise, avgAmountsPromise, dueDatePromise, projectionPromise])
                .then(([chartsDataResponse, avgAmountsResponse, dueDateResponse, projectionResponse]) => {
                    setChartData(chartsDataResponse.data);
                    setAvgAmountData(avgAmountsResponse.data);
                    setDueDateData(dueDateResponse.data);
                    setProjectionData(projectionResponse.data);
                })
                .catch(error => {
                    console.error("Error fetching chart data:", error);
                });
        }
    }, [selectedYear, selectedMonth]);

    if (!chartData) {
        return null;
    }

    const { money_results, num_results } = chartData;

    const transformData = (moneyData, numData) => {
        const transformed = [];
        const years = Object.keys(moneyData).filter(y => y !== 'total');
        const businessTypes = ['常规业务', '建行批量业务', '微众批量业务', '工行批量业务'];

        businessTypes.forEach(type => {
            const entry = { name: type };
            years.forEach(year => {
                entry[`${year}_money`] = moneyData[year][type] || 0;
                entry[`${year}_num`] = numData[year][type] || 0;
            });
            transformed.push(entry);
        });
        
        const totalEntry = { name: '整体' };
        years.forEach(year => {
            totalEntry[`${year}_money`] = (moneyData[year]['常规业务'] || 0) + (moneyData[year]['建行批量业务'] || 0) + (moneyData[year]['微众批量业务'] || 0) + (moneyData[year]['工行批量业务'] || 0);
            totalEntry[`${year}_num`] = (numData[year]['常规业务'] || 0) + (numData[year]['建行批量业务'] || 0) + (numData[year]['微众批量业务'] || 0) + (numData[year]['工行批量业务'] || 0);
        });
        transformed.push(totalEntry);

        return transformed;
    };

    const combinedData = transformData(money_results, num_results);
    const years = Object.keys(money_results).filter(y => y !== 'total');

    return (
        <>
            <Card>
                <Card.Header>
                    <h4>数据展示</h4>
                </Card.Header>
                <Card.Body>
                    <Row>
                        <Col md={12} className="mb-4">
                            <h5>新增借款金额（万元）</h5>
                            <ResponsiveContainer width="100%" height={400}>
                                <BarChart data={combinedData}>
                                    <CartesianGrid strokeDasharray="3 3" />
                                    <XAxis dataKey="name" />
                                    <YAxis />
                                    <Tooltip formatter={(value) => `${value.toLocaleString()} 万元`} />
                                    <Legend />
                                    {years.map((year, index) => (
                                        <Bar key={`${year}_money`} dataKey={`${year}_money`} fill={yearlyColors[index % yearlyColors.length]} name={`${year}年`} />
                                    ))}
                                </BarChart>
                            </ResponsiveContainer>
                        </Col>
                        <Col md={12} className="mb-4">
                            <h5>新增借款企业家数</h5>
                            <ResponsiveContainer width="100%" height={400}>
                                <BarChart data={combinedData}>
                                    <CartesianGrid strokeDasharray="3 3" />
                                    <XAxis dataKey="name" />
                                    <YAxis />
                                    <Tooltip formatter={(value) => `${value} 家`} />
                                    <Legend />
                                    {years.map((year, index) => (
                                        <Bar key={`${year}_num`} dataKey={`${year}_num`} fill={yearlyColors[index % yearlyColors.length]} name={`${year}年`} />
                                    ))}
                                </BarChart>
                            </ResponsiveContainer>
                        </Col>
                    </Row>
                </Card.Body>
            </Card>
            <BusinessProportionCharts chartData={chartData} />
            <AverageAmountChart avgAmountData={avgAmountData} />
            <DueDateChart dueDateData={dueDateData} />
            <BalanceProjectionChart projectionData={projectionData} />
        </>
    );
}

export default ChartsDisplay;
