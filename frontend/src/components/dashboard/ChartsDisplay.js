import React from 'react';
import { Card, Col, Row } from 'react-bootstrap';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line } from 'recharts';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#AF19FF', '#FF4560'];

function ChartsDisplay({ stats }) {
    if (!stats) {
        return null;
    }

    return (
        <Card>
            <Card.Header>
                <h4>数据展示</h4>
            </Card.Header>
            <Card.Body>
                <Row>
                    {/* By Bank Chart */}
                    <Col md={6} className="mb-4">
                        <h5>按合作银行统计</h5>
                        <ResponsiveContainer width="100%" height={300}>
                            <BarChart data={stats.by_bank}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="cooperative_bank" />
                                <YAxis />
                                <Tooltip formatter={(value) => value.toLocaleString()} />
                                <Legend />
                                <Bar dataKey="total_loan_amount" fill="#8884d8" name="贷款总额" />
                            </BarChart>
                        </ResponsiveContainer>
                    </Col>

                    {/* Loan Status Distribution Pie Chart */}
                    <Col md={6} className="mb-4">
                        <h5>借据状态分布</h5>
                        <ResponsiveContainer width="100%" height={300}>
                            <PieChart>
                                <Pie data={stats.loan_status_distribution} dataKey="count" nameKey="loan_status" cx="50%" cy="50%" outerRadius={100} fill="#8884d8" label>
                                    {stats.loan_status_distribution.map((entry, index) => <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />)}
                                </Pie>
                                <Tooltip />
                                <Legend />
                            </PieChart>
                        </ResponsiveContainer>
                    </Col>

                    {/* By Business Type Chart */}
                    <Col md={6}>
                        <h5>按业务类型统计</h5>
                        <ResponsiveContainer width="100%" height={300}>
                            <BarChart data={stats.by_type}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="business_type" />
                                <YAxis />
                                <Tooltip formatter={(value) => value.toLocaleString()} />
                                <Legend />
                                <Bar dataKey="total_loan_amount" fill="#82ca9d" name="贷款总额" />
                            </BarChart>
                        </ResponsiveContainer>
                    </Col>

                    {/* By Business Year Chart (Trend) */}
                    <Col md={6}>
                        <h5>按业务年度统计 (贷款总额)</h5>
                        <ResponsiveContainer width="100%" height={300}>
                            <LineChart data={stats.by_year}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="business_year" />
                                <YAxis />
                                <Tooltip formatter={(value) => value.toLocaleString()} />
                                <Legend />
                                <Line type="monotone" dataKey="total_loan_amount" stroke="#ffc658" name="贷款总额" />
                            </LineChart>
                        </ResponsiveContainer>
                    </Col>
                </Row>
            </Card.Body>
        </Card>
    );
}

export default ChartsDisplay;
