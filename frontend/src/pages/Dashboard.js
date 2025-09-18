import React, { useState, useEffect, useContext } from 'react';
import api from '../api';
import { DataContext } from '../DataContext';
import DataSlicer from '../components/DataSlicer';
import { Row, Col, Card } from 'react-bootstrap';
import ChartsDisplay from '../components/dashboard/ChartsDisplay';
import StatisticCard from '../components/dashboard/StatisticCard';
import { PiggyBank, ShieldCheck, Building, BuildingAdd, CashCoin, ShieldPlus, BuildingLock, Wallet2, ShieldShaded, GraphUpArrow, GraphUp, PersonAdd } from 'react-bootstrap-icons';

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
    const [monthlyGrowth, setMonthlyGrowth] = useState(null);
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

        const summaryPromise = api.get(`/api/analysis/summary`, { params });
        const monthlyGrowthPromise = api.get(`/api/analysis/monthly_growth`, { params });

        Promise.all([summaryPromise, monthlyGrowthPromise])
            .then(([summaryResponse, monthlyGrowthResponse]) => {
                setSummary(summaryResponse.data);
                setMonthlyGrowth(monthlyGrowthResponse.data);
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
                setMonthlyGrowth({
                    new_loan_amount: 0,
                    new_guarantee_amount: 0,
                    new_company_count: 0,
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
            <Row>
                {/* Data Display Section */}
                <Col lg={4}>
                    <Card className="h-100 shadow-sm">
                        <Card.Header className="bg-white border-0">
                            <h3 className="mb-0">数据总览</h3>
                        </Card.Header>
                        <Card.Body>
                            <Row>
                                <Col md={6}>
                                    <StatisticCard
                                        title="累计借款金额"
                                        value={`¥ ${summary?.cumulative_loan_amount?.toLocaleString()}`}
                                        icon={<PiggyBank size={32} />}
                                        color="primary"
                                    />
                                </Col>
                                <Col md={6}>
                                    <StatisticCard
                                        title="累计担保金额"
                                        value={`¥ ${summary?.cumulative_guarantee_amount?.toLocaleString()}`}
                                        icon={<ShieldCheck size={32} />}
                                        color="success"
                                    />
                                </Col>
                                <Col md={6}>
                                    <StatisticCard
                                        title="累计借款企业"
                                        value={summary?.cumulative_company_count?.toLocaleString()}
                                        icon={<Building size={32} />}
                                        color="info"
                                    />
                                </Col>
                                <Col md={6}>
                                    <StatisticCard
                                        title="本年新增企业"
                                        value={summary?.new_companies_this_year_count?.toLocaleString()}
                                        icon={<BuildingAdd size={32} />}
                                        color="warning"
                                    />
                                </Col>
                                <Col md={6}>
                                    <StatisticCard
                                        title="本年新增借款"
                                        value={`¥ ${summary?.new_companies_this_year_loan?.toLocaleString()}`}
                                        icon={<CashCoin size={32} />}
                                        color="danger"
                                    />
                                </Col>
                                <Col md={6}>
                                    <StatisticCard
                                        title="本年新增担保"
                                        value={`¥ ${summary?.new_companies_this_year_guarantee?.toLocaleString()}`}
                                        icon={<ShieldPlus size={32} />}
                                        color="danger"
                                    />
                                </Col>
                                <Col md={6}>
                                    <StatisticCard
                                        title="在保企业数量"
                                        value={summary?.in_force_companies_count?.toLocaleString()}
                                        icon={<BuildingLock size={32} />}
                                        color="primary"
                                    />
                                </Col>
                                <Col md={6}>
                                    <StatisticCard
                                        title="月新增贷款"
                                        value={`¥ ${monthlyGrowth?.new_loan_amount?.toLocaleString()}`}
                                        icon={<GraphUpArrow size={32} />}
                                        color="info"
                                    />
                                </Col>
                                <Col md={6}>
                                    <StatisticCard
                                        title="月新增担保"
                                        value={`¥ ${monthlyGrowth?.new_guarantee_amount?.toLocaleString()}`}
                                        icon={<GraphUp size={32} />}
                                        color="info"
                                    />
                                </Col>
                                <Col md={6}>
                                    <StatisticCard
                                        title="月新增企业"
                                        value={monthlyGrowth?.new_company_count?.toLocaleString()}
                                        icon={<PersonAdd size={32} />}
                                        color="info"
                                    />
                                </Col>
                                <Col md={6}>
                                    <StatisticCard
                                        title="借款余额"
                                        value={`¥ ${summary?.total_loan_balance?.toLocaleString()}`}
                                        icon={<Wallet2 size={32} />}
                                        color="success"
                                    />
                                </Col>
                                <Col md={6}>
                                    <StatisticCard
                                        title="担保余额"
                                        value={`¥ ${summary?.total_guarantee_balance?.toLocaleString()}`}
                                        icon={<ShieldShaded size={32} />}
                                        color="info"
                                    />
                                </Col>
                            </Row>
                        </Card.Body>
                    </Card>
                </Col>

                {/* Chart Display Section */}
                <Col lg={8}>
                    <ChartsDisplay />
                </Col>
            </Row>
        </div>
    );
}

export default Dashboard;
