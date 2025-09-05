import React from 'react';
import { Card, Col, Row } from 'react-bootstrap';

function StatisticsDisplay({ stats }) {
    if (!stats || !stats.monthly_growth) {
        return null;
    }

    return (
        <Card className="mb-4">
            <Card.Header>
                <h4>数据统计</h4>
            </Card.Header>
            <Card.Body>
                <Row>
                    <Col md={4}>
                        <h5>月度增长</h5>
                        <p className="mb-1"><strong>新增贷款金额:</strong> {stats.monthly_growth.new_loan_amount?.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</p>
                        <p className="mb-1"><strong>新增担保金额:</strong> {stats.monthly_growth.new_guarantee_amount?.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</p>
                        <p className="mb-0"><strong>新增企业数:</strong> {stats.monthly_growth.new_company_count}</p>
                    </Col>
                    </Row>
            </Card.Body>
        </Card>
    );
}

export default StatisticsDisplay;
