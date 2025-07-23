import React, { useState, useEffect, useContext } from 'react';
import axios from 'axios';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { DataContext } from '../DataContext'; // Import DataContext

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#AF19FF'];

function Dashboard() {
    const { selectedYear, selectedMonth } = useContext(DataContext); // Use context for year and month
    const [summary, setSummary] = useState(null);
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        setLoading(true);
        const fetchSummary = axios.get(`/api/analysis/summary?year=${selectedYear}&month=${selectedMonth}`);
        const fetchData = axios.get(`/api/data?per_page=1000&year=${selectedYear}&month=${selectedMonth}`); // Fetch data for charts

        Promise.all([fetchSummary, fetchData])
            .then(([summaryResponse, dataResponse]) => {
                setSummary(summaryResponse.data);
                setData(dataResponse.data.data);
                setLoading(false);
            })
            .catch(error => {
                console.error("加载数据时出错:", error);
                setLoading(false);
                // Fallback to empty data on error
                setSummary({
                    total_loan_amount: 0,
                    total_guarantee_amount: 0,
                    total_records: 0
                });
                setData([]);
            });
    }, [selectedYear, selectedMonth]); // Re-fetch when year or month changes

    const getBankStats = () => {
        const bankStats = data.reduce((acc, item) => {
            const bank = item.cooperative_bank || '未知银行';
            acc[bank] = (acc[bank] || 0) + (item.loan_amount || 0);
            return acc;
        }, {});
        return Object.keys(bankStats).map(bank => ({ name: bank, value: bankStats[bank] }));
    };

    const getStatusStats = () => {
        const statusStats = data.reduce((acc, item) => {
            const status = item.loan_status || '未知状态';
            acc[status] = (acc[status] || 0) + 1;
            return acc;
        }, {});
        return Object.keys(statusStats).map(status => ({ name: status, value: statusStats[status] }));
    };

    if (loading) {
        return <div>正在加载仪表盘...</div>;
    }

    return (
        <div className="container-fluid">
            <h2 className="my-4">业务数据仪表盘 - {selectedYear}年{selectedMonth}月</h2>
            <div className="row">
                {/* Data Display Section */}
                <div className="col-lg-4">
                    <div className="card">
                        <div className="card-header">
                            <h3>数据展示</h3>
                        </div>
                        <div className="card-body">
                            <div className="mb-3 p-3 bg-light rounded">
                                <h4>累计借款金额（万元）</h4>
                                <p className="h2 text-primary">¥ {summary?.cumulative_loan_amount?.toLocaleString()}</p>
                            </div>
                            <div className="mb-3 p-3 bg-light rounded">
                                <h4>累计担保金额（万元）</h4>
                                <p className="h2 text-success">¥ {summary?.cumulative_guarantee_amount?.toLocaleString()}</p>
                            </div>
                            <div className="mb-3 p-3 bg-light rounded">
                                <h4>累计借款企业数量</h4>
                                <p className="h2 text-info">{summary?.cumulative_company_count?.toLocaleString()}</p>
                            </div>
                            <div className="mb-3 p-3 bg-light rounded">
                                <h4>本年新增企业数量</h4>
                                <p className="h2 text-warning">{summary?.new_companies_this_year_count?.toLocaleString()}</p>
                            </div>
                            <div className="mb-3 p-3 bg-light rounded">
                                <h4>本年新增借款金额（万元）</h4>
                                <p className="h2 text-danger">¥ {summary?.new_companies_this_year_loan?.toLocaleString()}</p>
                            </div>
                            <div className="mb-3 p-3 bg-light rounded">
                                <h4>本年新增担保金额（万元）</h4>
                                <p className="h2 text-danger">¥ {summary?.new_companies_this_year_guarantee?.toLocaleString()}</p>
                            </div>
                            <div className="mb-3 p-3 bg-light rounded">
                                <h4>在保企业数量</h4>
                                <p className="h2 text-primary">{summary?.in_force_companies_count?.toLocaleString()}</p>
                            </div>
                            <div className="mb-3 p-3 bg-light rounded">
                                <h4>借款余额（万元）</h4>
                                <p className="h2 text-success">¥ {summary?.total_loan_balance?.toLocaleString()}</p>
                            </div>
                            <div className="p-3 bg-light rounded">
                                <h4>担保余额（万元）</h4>
                                <p className="h2 text-info">¥ {summary?.total_guarantee_balance?.toLocaleString()}</p>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Chart Display Section */}
                <div className="col-lg-8">
                    <div className="card">
                        <div className="card-header">
                            <h3>图表展示</h3>
                        </div>
                        <div className="card-body">
                            <div className="mb-5">
                                <h5>按合作银行统计贷款总额</h5>
                                <ResponsiveContainer width="100%" height={300}>
                                    <BarChart data={getBankStats()}>
                                        <CartesianGrid strokeDasharray="3 3" />
                                        <XAxis dataKey="name" />
                                        <YAxis />
                                        <Tooltip formatter={(value) => `¥ ${value.toLocaleString()}`} />
                                        <Legend />
                                        <Bar dataKey="value" fill="#8884d8" name="贷款总额" />
                                    </BarChart>
                                </ResponsiveContainer>
                            </div>
                            <div>
                                <h5>借据状态分布</h5>
                                <ResponsiveContainer width="100%" height={300}>
                                    <PieChart>
                                        <Pie data={getStatusStats()} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={100} fill="#82ca9d" label>
                                            {getStatusStats().map((entry, index) => (
                                                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                            ))}
                                        </Pie>
                                        <Tooltip formatter={(value, name) => `${value} (${(value / data.length * 100).toFixed(2)}%)`} />
                                        <Legend />
                                    </PieChart>
                                </ResponsiveContainer>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default Dashboard;