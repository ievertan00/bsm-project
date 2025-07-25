import React from 'react';
import { Form, Row, Col } from 'react-bootstrap';

function DateSelector({ 
    selectedYear, 
    selectedMonth, 
    availableYears, 
    availableMonths, 
    onYearChange, 
    onMonthChange 
}) {
    const monthsForSelectedYear = availableMonths
        .filter(m => m.year === selectedYear)
        .map(m => m.month)
        .sort((a, b) => a - b);

    return (
        <Form className="mb-4">
            <Row className="g-3 align-items-center">
                <Col xs="auto">
                    <Form.Label className="mb-0">年份:</Form.Label>
                </Col>
                <Col xs="auto">
                    <Form.Control
                        as="select"
                        size="sm"
                        value={selectedYear}
                        onChange={onYearChange}
                    >
                        {availableYears.map(year => (
                            <option key={year} value={year}>{year}年</option>
                        ))}
                    </Form.Control>
                </Col>
                <Col xs="auto">
                    <Form.Label className="mb-0">月份:</Form.Label>
                </Col>
                <Col xs="auto">
                    <Form.Control
                        as="select"
                        size="sm"
                        value={selectedMonth}
                        onChange={onMonthChange}
                    >
                        {monthsForSelectedYear.length > 0 ? (
                            monthsForSelectedYear.map(month => (
                                <option key={month} value={month}>{month}月</option>
                            ))
                        ) : (
                            <option value="">无数据</option>
                        )}
                    </Form.Control>
                </Col>
            </Row>
        </Form>
    );
}

export default DateSelector;
