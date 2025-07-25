import React, { useState, useEffect, useContext } from 'react';
import axios from 'axios';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { DataContext } from '../DataContext';
import DataSlicer from '../components/DataSlicer';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#AF19FF'];

function Dashboard() {
    const { availableYears, availableMonths } = useContext(DataContext);
    
    // Slicer states
    const [selectedYear, setSelectedYear] = useState(null);
    const [selectedMonth, setSelectedMonth] = useState(null);
    const [selectedBusinessType, setSelectedBusinessType] = useState('');
    const [selectedCooperativeBank, setSelectedCooperativeBank] = useState('');
    const [selectedIsTechnologyEnterprise, setSelectedIsTechnologyEnterprise] = useState('N/A'); // 'N/A', true, false

    // Options for slicers
    const [businessTypesOptions, setBusinessTypesOptions] = useState([]);
    const [cooperativeBanksOptions, setCooperativeBanksOptions] = useState([]);
    const [isTechnologyEnterpriseOptions, setIsTechnologyEnterpriseOptions] = useState([]);

    const [summary, setSummary] = useState(null);
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(true);

    // Fetch slicer options on component mount
    useEffect(() => {
        axios.get('/api/slicer-options')
            .then(response => {
                setBusinessTypesOptions(response.data.business_types);
                setCooperativeBanksOptions(response.data.cooperative_banks);
                setIsTechnologyEnterpriseOptions(response.data.is_technology_enterprise_options);
            })
            .catch(error => {
                console.error("Error fetching slicer options:", error);
            });
    }, []);

    // Set initial selected date to the latest available date once the context provides the available dates
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

    // Fetch data based on slicer selections
    useEffect(() => {
        if (!selectedYear || !selectedMonth) return; // Wait until initial date is set

        setLoading(true);
        const params = {
            year: selectedYear,
            month: selectedMonth,
            business_type: selectedBusinessType || undefined,
            cooperative_bank: selectedCooperativeBank || undefined,
            is_technology_enterprise: selectedIsTechnologyEnterprise === 'N/A' ? undefined : selectedIsTechnologyEnterprise
        };

        const fetchSummary = axios.get(`/api/analysis/summary`, { params });
        const fetchData = axios.get(`/api/data?per_page=1000`, { params });

        Promise.all([fetchSummary, fetchData])
            .then(([summaryResponse, dataResponse]) => {
                setSummary(summaryResponse.data);
                setData(dataResponse.data.data);
                setLoading(false);
            })
            .catch(error => {
                console.error("加载数据时出错:", error);
                setLoading(false);
                setSummary({
                    cumulative_loan_amount: 0,
                    cumulative_guarantee_amount: 0,
                    cumulative_company_count: 0,
                    new_companies_this_year_count: 0,
                    new_companies_this_year_loan: 0,
                    new_companies_this_year_guarantee: 0,
                    in_force_companies_count: 0,
                    total_loan_balance: 0,
                    total_guarantee_balance: 0,
                });
                setData([]);
            });
    }, [selectedYear, selectedMonth, selectedBusinessType, selectedCooperativeBank, selectedIsTechnologyEnterprise]);

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

    const handleBusinessTypeChange = (e) => {
        setSelectedBusinessType(e.target.value);
    };

    const handleCooperativeBankChange = (e) => {
        setSelectedCooperativeBank(e.target.value);
    };

    const handleIsTechnologyEnterpriseChange = (e) => {
        const value = e.target.value;
        if (value === 'true') {
            setSelectedIsTechnologyEnterprise(true);
        } else if (value === 'false') {
            setSelectedIsTechnologyEnterprise(false);
        } else if (value === 'all') {
            setSelectedIsTechnologyEnterprise(null);
        } else {
            setSelectedIsTechnologyEnterprise('N/A'); // Fallback for unexpected values
        }
    };

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
            <DataSlicer 
                selectedYear={selectedYear}
                selectedMonth={selectedMonth}
                selectedBusinessType={selectedBusinessType}
                selectedCooperativeBank={selectedCooperativeBank}
                selectedIsTechnologyEnterprise={selectedIsTechnologyEnterprise}
                availableYears={availableYears}
                availableMonths={availableMonths}
                businessTypesOptions={businessTypesOptions}
                cooperativeBanksOptions={cooperativeBanksOptions}
                isTechnologyEnterpriseOptions={isTechnologyEnterpriseOptions}
                onYearChange={handleYearChange}
                onMonthChange={handleMonthChange}
                onBusinessTypeChange={handleBusinessTypeChange}
                onCooperativeBankChange={handleCooperativeBankChange}
                onIsTechnologyEnterpriseChange={handleIsTechnologyEnterpriseChange}
            />
            <div className="row">
                {/* Data Display Section */}
                <div className="col-lg-4">
                    <div className="card">
                        <div className="card-header">
                            <h3>数据展示</h3>
                        </div>
                        <div className="card-body">
                            {/* Summary data display */}
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
