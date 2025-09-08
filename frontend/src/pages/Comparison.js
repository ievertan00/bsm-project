import React, { useState, useEffect } from 'react';
import { Button, Card, Col, Form, Row, ListGroup, Badge, Alert } from 'react-bootstrap';
import api from '../api';

function Comparison() {
    const [yearMonths, setYearMonths] = useState([]);
    const [ym1, setYm1] = useState('');
    const [ym2, setYm2] = useState('');
    const [comparison, setComparison] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    useEffect(() => {
        api.get('/api/available-dates')
            .then(response => {
                const formattedDates = response.data.months
                    .map(item => `${item.year}-${String(item.month).padStart(2, '0')}`)
                    .sort();
                setYearMonths(formattedDates);
            })
            .catch(err => {
                console.error("Error fetching available dates:", err);
                setError(err.response ? err.response.data.error : '无法连接到服务器');
            });
    }, []);

    const handleCompare = () => {
        setLoading(true);
        setError('');
        setComparison(null);
        api.get(`/api/compare?year_month1=${ym1}&year_month2=${ym2}`)
            .then(response => {
                if (response.data.error) {
                    setError(response.data.error);
                } else {
                    setComparison(response.data);
                }
                setLoading(false);
            })
            .catch(err => {
                setError(err.response ? err.response.data.error : '获取对比数据时发生错误。');
                setLoading(false);
            });
    };

    const renderPercentageBadge = (percentage) => {
        if (percentage === null || isNaN(percentage) || percentage === 999999.0) {
            return <Badge bg="success">新增</Badge>;
        }
        const bg = percentage >= 0 ? "success" : "danger";
        const sign = percentage > 0 ? "+" : "";
        return <Badge bg={bg}>{sign}{percentage.toFixed(2)}%</Badge>;
    };

    const renderSummary = (title, summary, percentages) => (
        <Col md={4}>
            <Card>
                <Card.Header as="h5">{title}</Card.Header>
                <ListGroup variant="flush">
                    {/* Summary items */}
                    <ListGroup.Item className="d-flex justify-content-between align-items-center">
                        总借款金额： {summary.total_loan_amount.toFixed(2)}
                        {percentages && renderPercentageBadge(percentages.total_loan_amount)}
                    </ListGroup.Item>
                    <ListGroup.Item className="d-flex justify-content-between align-items-center">
                        总担保金额： {summary.total_guarantee_amount.toFixed(2)}
                        {percentages && renderPercentageBadge(percentages.total_guarantee_amount)}
                    </ListGroup.Item>
                    <ListGroup.Item className="d-flex justify-content-between align-items-center">
                        本年新增借款金额： {summary.new_companies_this_year_loan.toFixed(2)}
                        {percentages && renderPercentageBadge(percentages.new_companies_this_year_loan)}
                    </ListGroup.Item>
                    <ListGroup.Item className="d-flex justify-content-between align-items-center">
                        本年新增担保金额： {summary.new_companies_this_year_guarantee_amount.toFixed(2)}
                        {percentages && renderPercentageBadge(percentages.new_companies_this_year_guarantee_amount)}
                    </ListGroup.Item>
                    <ListGroup.Item className="d-flex justify-content-between align-items-center">
                        本年新增企业数量： {summary.new_companies_this_year_count}
                        {percentages && renderPercentageBadge(percentages.new_companies_this_year_count)}
                    </ListGroup.Item>
                    <ListGroup.Item className="d-flex justify-content-between align-items-center">
                        借款余额： {summary.total_loan_balance.toFixed(2)}
                        {percentages && renderPercentageBadge(percentages.total_loan_balance)}
                    </ListGroup.Item>
                    <ListGroup.Item className="d-flex justify-content-between align-items-center">
                        担保余额： {summary.total_guarantee_balance.toFixed(2)}
                        {percentages && renderPercentageBadge(percentages.total_guarantee_balance)}
                    </ListGroup.Item>
                    <ListGroup.Item className="d-flex justify-content-between align-items-center">
                        业务数量： {summary.business_count}
                        {percentages && renderPercentageBadge(percentages.business_count)}
                    </ListGroup.Item>
                    <ListGroup.Item className="d-flex justify-content-between align-items-center">
                        独立公司数量： {summary.company_count}
                        {percentages && renderPercentageBadge(percentages.company_count)}
                    </ListGroup.Item>
                </ListGroup>
            </Card>
        </Col>
    );

    const formatNumber = (value) => {
        return typeof value === 'number' ? value.toFixed(2) : 'N/A';
    };

    const formatCount = (value) => {
        return typeof value === 'number' ? value : 'N/A';
    };

    

    const renderChangesSummary = (changes, percentages) => {
        if (!changes || !percentages) {
            return null;
        }
        return (
            <Col md={4}>
                <Card>
                    <Card.Header as="h5">变动概览</Card.Header>
                    <ListGroup variant="flush">
                        {/* Change summary items */}
                        <ListGroup.Item className="d-flex justify-content-between align-items-center">
                            总借款金额变动: {formatNumber(changes.total_loan_amount_change)}
                            {percentages && renderPercentageBadge(percentages.total_loan_amount)}
                        </ListGroup.Item>
                        <ListGroup.Item className="d-flex justify-content-between align-items-center">
                            总担保金额变动: {formatNumber(changes.total_guarantee_amount_change)}
                            {percentages && renderPercentageBadge(percentages.total_guarantee_amount)}
                        </ListGroup.Item>
                        <ListGroup.Item className="d-flex justify-content-between align-items-center">
                            本年新增借款金额变动: {formatNumber(changes.new_companies_this_year_loan_change)}
                            {percentages && renderPercentageBadge(percentages.new_companies_this_year_loan)}
                        </ListGroup.Item>
                         <ListGroup.Item className="d-flex justify-content-between align-items-center">
                            本年新增担保金额变动: {formatNumber(changes.new_companies_this_year_guarantee_amount_change)}
                            {percentages && renderPercentageBadge(percentages.new_companies_this_year_guarantee_amount)}
                        </ListGroup.Item>
                         <ListGroup.Item className="d-flex justify-content-between align-items-center">
                            本年新增企业数量变动: {formatCount(changes.new_companies_this_year_count_change)}
                            {percentages && renderPercentageBadge(percentages.new_companies_this_year_count)}
                        </ListGroup.Item>
                        <ListGroup.Item className="d-flex justify-content-between align-items-center">
                            借款余额变动: {formatNumber(changes.total_loan_balance_change)}
                            {percentages && renderPercentageBadge(percentages.total_loan_balance)}
                        </ListGroup.Item>
                        <ListGroup.Item className="d-flex justify-content-between align-items-center">
                            担保余额变动: {formatNumber(changes.total_guarantee_balance_change)}
                            {percentages && renderPercentageBadge(percentages.total_guarantee_balance)}
                        </ListGroup.Item>
                        <ListGroup.Item className="d-flex justify-content-between align-items-center">
                            业务数量变动: {formatCount(changes.business_count_change)}
                            {percentages && renderPercentageBadge(percentages.business_count)}
                        </ListGroup.Item>
                        <ListGroup.Item className="d-flex justify-content-between align-items-center">
                            独立公司数量变动: {formatCount(changes.company_count_change)}
                            {percentages && renderPercentageBadge(percentages.company_count)}
                        </ListGroup.Item>
                    </ListGroup>
                </Card>
            </Col>
        );
    };

    const renderCompanyCard = (title, companies, totalLoan) => (
        <Col md={6}>
            <Card>
                <Card.Header as="h5">{title} ({companies.length})</Card.Header>
                <ListGroup variant="flush" style={{maxHeight: '200px', overflowY: 'auto'}}>
                    {companies.map(c => (
                        <ListGroup.Item key={c.id || c.company_name} className="d-flex justify-content-between">
                            <span>{c.company_name}</span>
                            <Badge bg="info">{formatNumber(c.loan_amount)}</Badge>
                        </ListGroup.Item>
                    ))}
                </ListGroup>
                <Card.Footer>
                    总借款金额： {formatNumber(totalLoan)} | 新增企业家数： {companies.length}
                </Card.Footer>
            </Card>
        </Col>
    );

    const newTechCompanies = comparison?.company_analysis.new_companies.filter(c => c.is_technology_enterprise) || [];
    const newTechCompaniesLoan = newTechCompanies.reduce((sum, c) => sum + (c.loan_amount || 0), 0);

    return (
        <Card>
            <Card.Header><h3>版本对比</h3></Card.Header>
            <Card.Body>
                {error && (
                    <Alert variant="danger" onClose={() => setError('')} dismissible>
                        <Alert.Heading>Oh snap! You got an error!</Alert.Heading>
                        <p>{error}</p>
                    </Alert>
                )}
                <Row className="mb-3">
                    <Col md={4}>
                        <Form.Select value={ym1} onChange={(e) => setYm1(e.target.value)}>
                            <option>选择期间 1</option>
                            {yearMonths.map(ym => <option key={`ym1-${ym}`} value={ym}>{ym}</option>)}
                        </Form.Select>
                    </Col>
                    <Col md={4}>
                        <Form.Select value={ym2} onChange={(e) => setYm2(e.target.value)}>
                            <option>选择期间 2</option>
                            {yearMonths.map(ym => <option key={`ym2-${ym}`} value={ym}>{ym}</option>)}
                        </Form.Select>
                    </Col>
                    <Col md={4}>
                        <Button onClick={handleCompare} disabled={!ym1 || !ym2 || loading}>
                            {loading ? '正在对比...' : '对比'}
                        </Button>
                    </Col>
                </Row>

                {comparison && (
                    <div className="mt-4">
                        <Row>
                            {renderSummary(ym1, comparison.summary1, null)}
                            {renderSummary(ym2, comparison.summary2, null)}
                            {renderChangesSummary(comparison.changes, comparison.percentage_changes)}
                        </Row>
                        <hr />
                        <Row className="mt-4">
                            {renderCompanyCard(
                                "新增公司", 
                                comparison.company_analysis.new_companies, 
                                comparison.company_analysis.new_companies_loan
                            )}
                            {renderCompanyCard(
                                "新增科技型公司", 
                                newTechCompanies, 
                                newTechCompaniesLoan
                            )}
                        </Row>
                    </div>
                )}
            </Card.Body>
        </Card>
    );
}

export default Comparison;
