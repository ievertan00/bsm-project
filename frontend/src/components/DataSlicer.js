import React from 'react';
import { Form, Row, Col } from 'react-bootstrap';

function DataSlicer({
    selectedYear,
    selectedMonth,
    selectedBusinessType,
    selectedCooperativeBank,
    selectedIsTechnologyEnterprise,
    availableYears,
    availableMonths,
    businessTypesOptions,
    cooperativeBanksOptions,
    isTechnologyEnterpriseOptions,
    onYearChange,
    onMonthChange,
    onBusinessTypeChange,
    onCooperativeBankChange,
    onIsTechnologyEnterpriseChange
}) {
    const monthsForSelectedYear = availableMonths
        .filter(m => m.year === selectedYear)
        .map(m => m.month)
        .sort((a, b) => a - b);

    return (
        <Form className="mb-4">
            <Row className="g-3 align-items-center">
                {/* Data Snapshot Selector */}
                <Col xs="auto">
                    <Form.Label className="mb-0">数据快照:</Form.Label>
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

                {/* Business Type Selector */}
                <Col xs="auto">
                    <Form.Label className="mb-0">业务类型:</Form.Label>
                </Col>
                <Col xs="auto">
                    <Form.Control
                        as="select"
                        size="sm"
                        value={selectedBusinessType || ''}
                        onChange={onBusinessTypeChange}
                    >
                        <option value="">所有</option>
                        {businessTypesOptions.map(type => (
                            <option key={type} value={type}>{type}</option>
                        ))}
                    </Form.Control>
                </Col>

                {/* Cooperative Bank Selector */}
                <Col xs="auto">
                    <Form.Label className="mb-0">合作银行:</Form.Label>
                </Col>
                <Col xs="auto">
                    <Form.Control
                        as="select"
                        size="sm"
                        value={selectedCooperativeBank || ''}
                        onChange={onCooperativeBankChange}
                    >
                        <option value="">所有</option>
                        {cooperativeBanksOptions.map(bank => (
                            <option key={bank} value={bank}>{bank}</option>
                        ))}
                    </Form.Control>
                </Col>

                {/* Technology Enterprise Selector */}
                <Col xs="auto">
                    <Form.Label className="mb-0">科技企业:</Form.Label>
                </Col>
                <Col xs="auto">
                    <Form.Control
                        as="select"
                        size="sm"
                        value={selectedIsTechnologyEnterprise === true ? 'true' : (selectedIsTechnologyEnterprise === false ? 'false' : 'all')}
                        onChange={onIsTechnologyEnterpriseChange}
                    >
                        {isTechnologyEnterpriseOptions.map(option => (
                            <option key={option.value} value={option.value}>{option.label}</option>
                        ))}
                    </Form.Control>
                </Col>
            </Row>
        </Form>
    );
}

export default DataSlicer;
