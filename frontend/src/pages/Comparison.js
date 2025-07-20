
import React, { useState } from 'react';
import axios from 'axios';
import { Button, Card, Col, Form, Row, ListGroup, Badge } from 'react-bootstrap';

function Comparison({ yearMonths }) {
    const [ym1, setYm1] = useState('');
    const [ym2, setYm2] = useState('');
    const [comparison, setComparison] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleCompare = () => {
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
                setError("An error occurred while fetching comparison data.");
                setLoading(false);
            });
    };

    const renderPercentageBadge = (percentage) => {
        if (percentage === Infinity) {
            return <Badge bg="success">New</Badge>;
        }
        const bg = percentage >= 0 ? "success" : "danger";
        const sign = percentage > 0 ? "+" : "";
        return <Badge bg={bg}>{sign}{percentage.toFixed(2)}%</Badge>;
    };

    const renderSummary = (title, summary, percentages) => (
        <Col md={6}>
            <Card>
                <Card.Header as="h5">{title}</Card.Header>
                <ListGroup variant="flush">
                    <ListGroup.Item className="d-flex justify-content-between align-items-center">
                        Total Loan: {summary.total_loan_amount.toFixed(2)}
                        {percentages && renderPercentageBadge(percentages.total_loan_amount)}
                    </ListGroup.Item>
                    <ListGroup.Item className="d-flex justify-content-between align-items-center">
                        Total Guarantee: {summary.total_guarantee_amount.toFixed(2)}
                        {percentages && renderPercentageBadge(percentages.total_guarantee_amount)}
                    </ListGroup.Item>
                    <ListGroup.Item className="d-flex justify-content-between align-items-center">
                        Loan Balance: {summary.total_loan_balance.toFixed(2)}
                        {percentages && renderPercentageBadge(percentages.total_loan_balance)}
                    </ListGroup.Item>
                    <ListGroup.Item className="d-flex justify-content-between align-items-center">
                        Guarantee Balance: {summary.total_guarantee_balance.toFixed(2)}
                        {percentages && renderPercentageBadge(percentages.total_guarantee_balance)}
                    </ListGroup.Item>
                    <ListGroup.Item className="d-flex justify-content-between align-items-center">
                        Business Count: {summary.business_count}
                        {percentages && renderPercentageBadge(percentages.business_count)}
                    </ListGroup.Item>
                    <ListGroup.Item className="d-flex justify-content-between align-items-center">
                        Unique Companies: {summary.company_count}
                        {percentages && renderPercentageBadge(percentages.company_count)}
                    </ListGroup.Item>
                </ListGroup>
            </Card>
        </Col>
    );

    return (
        <Card>
            <Card.Header><h3>Version Comparison</h3></Card.Header>
            <Card.Body>
                <Row className="mb-3">
                    <Col md={4}>
                        <Form.Select value={ym1} onChange={(e) => setYm1(e.target.value)}>
                            <option>Select Period 1</option>
                            {yearMonths.map(ym => <option key={`ym1-${ym}`} value={ym}>{ym}</option>)}
                        </Form.Select>
                    </Col>
                    <Col md={4}>
                        <Form.Select value={ym2} onChange={(e) => setYm2(e.target.value)}>
                            <option>Select Period 2</option>
                            {yearMonths.map(ym => <option key={`ym2-${ym}`} value={ym}>{ym}</option>)}
                        </Form.Select>
                    </Col>
                    <Col md={4}>
                        <Button onClick={handleCompare} disabled={!ym1 || !ym2 || loading}>
                            {loading ? 'Comparing...' : 'Compare'}
                        </Button>
                    </Col>
                </Row>

                {error && <div className="alert alert-danger">{error}</div>}

                {comparison && (
                    <div className="mt-4">
                        <Row>
                            {renderSummary(ym1, comparison.summary1, null)}
                            {renderSummary(ym2, comparison.summary2, comparison.percentage_changes)}
                        </Row>
                        <hr />
                        <Row className="mt-4">
                            <Col md={4}>
                                <Card>
                                    <Card.Header as="h5">New Companies ({comparison.company_analysis.new_companies_count})</Card.Header>
                                    <ListGroup variant="flush" style={{maxHeight: '200px', overflowY: 'auto'}}>
                                        {comparison.company_analysis.new_companies.map(c => <ListGroup.Item key={c}>{c}</ListGroup.Item>)}
                                    </ListGroup>
                                    <Card.Footer>Total Loan: {comparison.company_analysis.new_companies_loan.toFixed(2)}</Card.Footer>
                                </Card>
                            </Col>
                            <Col md={4}>
                                <Card>
                                    <Card.Header as="h5">Lost Companies ({comparison.company_analysis.lost_companies_count})</Card.Header>
                                    <ListGroup variant="flush" style={{maxHeight: '200px', overflowY: 'auto'}}>
                                        {comparison.company_analysis.lost_companies.map(c => <ListGroup.Item key={c}>{c}</ListGroup.Item>)}
                                    </ListGroup>
                                    <Card.Footer>Total Loan: {comparison.company_analysis.lost_companies_loan.toFixed(2)}</Card.Footer>
                                </Card>
                            </Col>
                            <Col md={4}>
                                <Card>
                                    <Card.Header as="h5">Continuing Companies ({comparison.company_analysis.continuing_companies_count})</Card.Header>
                                    <Card.Body>
                                        <p>Loan Change: 
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
