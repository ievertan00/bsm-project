import React, { useState, useEffect, useContext } from 'react';
import api from '../api';
import { DataContext } from '../DataContext';
import DataSlicer from '../components/DataSlicer';
import ChartsDisplay from '../components/dashboard/ChartsDisplay';

function Dashboard() {
    const { availableYears, availableMonths, selectedYear, selectedMonth, setSelectedYear, setSelectedMonth } = useContext(DataContext);
    
    // Slicer states
    const [selectedBusinessType, setSelectedBusinessType] = useState('');
    const [selectedCooperativeBank, setSelectedCooperativeBank] = useState('');
    const [selectedIsTechnologyEnterprise, setSelectedIsTechnologyEnterprise] = useState('N/A'); // 'N/A', true, false

    // Options for slicers
    const [businessTypesOptions, setBusinessTypesOptions] = useState([]);
    const [cooperativeBanksOptions, setCooperativeBanksOptions] = useState([]);
    const [isTechnologyEnterpriseOptions, setIsTechnologyEnterpriseOptions] = useState([]);

    const [summary, setSummary] = useState(null);
    const [loading, setLoading] = useState(true);

    // Fetch slicer options on component mount
    useEffect(() => {
        api.get('/api/slicer-options')
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
        if (availableYears && availableYears.length > 0 && !selectedYear) {
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
    }, [availableYears, availableMonths, selectedYear, setSelectedYear, setSelectedMonth]);

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

        api.get(`/api/analysis/summary`, { params })
            .then(response => {
                setSummary(response.data);
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
                    <div className="card h-100">
                        <div className="card-header">
                            <h3>数据展示</h3>
                        </div>
                        <div className="card-body">
                            <Row>
                                <Col md={6} className="mb-3">
                                    <div className="p-3 bg-light rounded">
                                        <h4>累计借款金额（万元）</h4>
                                        <p className="h2 text-primary">¥ {summary?.cumulative_loan_amount?.toLocaleString()}</p>
                                    </div>
                                </Col>
                                <Col md={6} className="mb-3">
                                    <div className="p-3 bg-light rounded">
                                        <h4>累计担保金额（万元）</h4>
                                        <p className="h2 text-success">¥ {summary?.cumulative_guarantee_amount?.toLocaleString()}</p>
                                    </div>
                                </Col>
                                <Col md={6} className="mb-3">
                                    <div className="p-3 bg-light rounded">
                                        <h4>累计借款企业数量</h4>
                                        <p className="h2 text-info">{summary?.cumulative_company_count?.toLocaleString()}</p>
                                    </div>
                                </Col>
                                <Col md={6} className="mb-3">
                                    <div className="p-3 bg-light rounded">
                                        <h4>本年新增企业数量</h4>
                                        <p className="h2 text-warning">{summary?.new_companies_this_year_count?.toLocaleString()}</p>
                                    </div>
                                </Col>
                                <Col md={6} className="mb-3">
                                    <div className="p-3 bg-light rounded">
                                        <h4>本年新增借款金额（万元）</h4>
                                        <p className="h2 text-danger">¥ {summary?.new_companies_this_year_loan?.toLocaleString()}</p>
                                    </div>
                                </Col>
                                <Col md={6} className="mb-3">
                                    <div className="p-3 bg-light rounded">
                                        <h4>本年新增担保金额（万元）</h4>
                                        <p className="h2 text-danger">¥ {summary?.new_companies_this_year_guarantee?.toLocaleString()}</p>
                                    </div>
                                </Col>
                                <Col md={6} className="mb-3">
                                    <div className="p-3 bg-light rounded">
                                        <h4>在保企业数量</h4>
                                        <p className="h2 text-primary">{summary?.in_force_companies_count?.toLocaleString()}</p>
                                    </div>
                                </Col>
                                <Col md={6} className="mb-3">
                                    <div className="p-3 bg-light rounded">
                                        <h4>借款余额（万元）</h4>
                                        <p className="h2 text-success">¥ {summary?.total_loan_balance?.toLocaleString()}</p>
                                    </div>
                                </Col>
                                <Col md={12} className="mb-3">
                                    <div className="p-3 bg-light rounded">
                                        <h4>担保余额（万元）</h4>
                                        <p className="h2 text-info">¥ {summary?.total_guarantee_balance?.toLocaleString()}</p>
                                    </div>
                                </Col>
                            </Row>
                        </div>
                    </div>
                </div>

                {/* Chart Display Section */}
                <div className="col-lg-8">
                    <ChartsDisplay />
                </div>
            </div>
        </div>
    );
}

export default Dashboard;
