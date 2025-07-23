
import React, { useState } from 'react';
import axios from 'axios';
import { Button, Card, Col, Form, Row, ListGroup, Badge } from 'react-bootstrap';

function Comparison({ yearMonths }) {
    const [ym1, setYm1] = useState('');
    const [ym2, setYm2] = useState('');
    const [comparison, setComparison] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handle对比 = () => {
        setLoading(true);
        setError('');
        setComparison(null);
        axios.get(`/api/compare?year_month1=${ym1}&year_month2=${ym2}`)
            .then(response => {
                if (response.data.error) {
                    setError(response.data.error);
                } else {
                    setComparison(response.data);
                }
                setLoading(false);
            })
            .catch(err => {
                setError("获取对比数据时发生错误。");
                setLoading(false);
            });
    };

    const renderPercentageBadge = (percentage) => {
        if (percentage === Infinity) {
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
                        本年新增担保金额： {summary.new_companies_this_year_guarantee.toFixed(2)}
                        {percentages && renderPercentageBadge(percentages.new_companies_this_year_guarantee)}
                    </ListGroup.Item>
                    <ListGroup.Item className="d-flex justify-content-between align-items-center">
                        本年新增企业数量： {summary.new_companies_this_year_count.toFixed(2)}
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
            return null; // Or a loading indicator, or a message
        }
        return (
            <Col md={4}>
                <Card>
                    <Card.Header as="h5">变动概览</Card.Header>
                    <ListGroup variant="flush">
                        <ListGroup.Item className="d-flex justify-content-between align-items-center">
                            总借款金额变动: {formatNumber(changes.total_loan_amount_change)}
                            {percentages && renderPercentageBadge(percentages.total_loan_amount)}
                        </ListGroup.Item>
                        <ListGroup.Item className="d-flex justify-content-between align-items-center">
                            总担保金额变动: {formatNumber(changes.total_guarantee_amount_change)}
                            {percentages && renderPercentageBadge(percentages.total_guarantee_amount)}
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

    return (
        <Card>
            <Card.Header><h3>版本对比</h3></Card.Header>
            <Card.Body>
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
                        <Button onClick={handle对比} disabled={!ym1 || !ym2 || loading}>
                            {loading ? '正在对比...' : '对比'}
                        </Button>
                    </Col>
                </Row>

                {error && <div className="alert alert-danger">{error}</div>}

                {comparison && (
                    <div className="mt-4">
                        <Row>
                            {renderSummary(ym1, comparison.summary1, null)}
                            {renderSummary(ym2, comparison.summary2, null)}
                            {renderChangesSummary(comparison.changes, comparison.percentage_changes)}
                        </Row>
                        <hr />
                        <Row className="mt-4">
                            <Col md={4}>
                                <Card>
                                    <Card.Header as="h5">新增公司 ({comparison.company_analysis.new_companies_count})</Card.Header>
                                    <ListGroup variant="flush" style={{maxHeight: '200px', overflowY: 'auto'}}>
                                        {comparison.company_analysis.new_companies.map(c => <ListGroup.Item key={c}>{c}</ListGroup.Item>)}
                                    </ListGroup>
                                    <Card.Footer>总借款金额： {comparison.company_analysis.new_companies_loan.toFixed(2)}</Card.Footer>
                                </Card>
                            </Col>
                            <Col md={4}>
                                <Card>
                                    <Card.Header as="h5">流失公司 ({comparison.company_analysis.lost_companies_count})</Card.Header>
                                    <ListGroup variant="flush" style={{maxHeight: '200px', overflowY: 'auto'}}>
                                        {comparison.company_analysis.lost_companies.map(c => <ListGroup.Item key={c}>{c}</ListGroup.Item>)}
                                    </ListGroup>
                                    <Card.Footer>总借款金额： {comparison.company_analysis.lost_companies_loan.toFixed(2)}</Card.Footer>
                                </Card>
                            </Col>
                            <Col md={4}>
                                <Card>
                                    <Card.Header as="h5">持续合作公司 ({comparison.company_analysis.continuing_companies_count})</Card.Header>
                                    <Card.Body>
                                        <p>借款变化： 
                                            <Badge bg={comparison.company_analysis.continuing_companies_loan_change >= 0 ? "success" : "danger"}>
                                                {comparison.company_analysis.continuing_companies_loan_change.toFixed(2)}
                                            </Badge>
                                        </p>
                                    </Card.Body>
                                </Card>
                            </Col>
                        </Row>
                    </div>
                )}
            </Card.Body>
        </Card>
    );
}

export default Comparison;
