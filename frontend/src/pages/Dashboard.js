
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line } from 'recharts';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

function Dashboard({ yearMonth }) {
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (yearMonth) {
            setLoading(true);
            axios.get(`/api/statistics?year_month=${yearMonth}`)
                .then(response => {
                    setStats(response.data);
                    setLoading(false);
                })
                .catch(error => {
                    console.error("Error fetching statistics:", error);
                    setLoading(false);
                });
        }
    }, [yearMonth]);

    if (loading) {
        return <div>Loading statistics...</div>;
    }

    if (!stats || Object.keys(stats).length === 0) {
        return <div className="alert alert-warning">No data available for the selected period.</div>;
    }

    return (
        <div className="card mt-4">
            <div className="card-header">
                <h3>Dashboard for {yearMonth}</h3>
            </div>
            <div className="card-body">
                <div className="row">
                    {/* Monthly Growth Stats */}
                    <div className="col-md-12 mb-4">
                        <h4>Monthly Growth</h4>
                        <p>New Loan Amount: {stats.monthly_growth?.new_loan_amount?.toFixed(2)}</p>
                        <p>New Guarantee Amount: {stats.monthly_growth?.new_guarantee_amount?.toFixed(2)}</p>
                        <p>New Companies: {stats.monthly_growth?.new_company_count}</p>
                    </div>

                    {/* By Bank Chart */}
                    <div className="col-md-6">
                        <h5>By Bank</h5>
                        <ResponsiveContainer width="100%" height={300}>
                            <BarChart data={stats.by_bank}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="cooperation_bank" />
                                <YAxis />
                                <Tooltip />
                                <Legend />
                                <Bar dataKey="total_loan_amount" fill="#8884d8" name="Loan Amount" />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>

                    {/* Loan Status Distribution Pie Chart */}
                    <div className="col-md-6">
                        <h5>Loan Status Distribution</h5>
                        <ResponsiveContainer width="100%" height={300}>
                            <PieChart>
                                <Pie data={stats.loan_status_distribution} dataKey="count" nameKey="loan_status" cx="50%" cy="50%" outerRadius={100} fill="#8884d8" label>
                                    {stats.loan_status_distribution.map((entry, index) => <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />)}
                                </Pie>
                                <Tooltip />
                                <Legend />
                            </PieChart>
                        </ResponsiveContainer>
                    </div>

                    {/* By Business Type Chart */}
                    <div className="col-md-6 mt-4">
                        <h5>By Business Type</h5>
                        <ResponsiveContainer width="100%" height={300}>
                            <BarChart data={stats.by_type}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="business_type" />
                                <YAxis />
                                <Tooltip />
                                <Legend />
                                <Bar dataKey="total_loan_amount" fill="#82ca9d" name="Loan Amount" />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>

                    {/* By Business Year Chart (Trend) */}
                    <div className="col-md-6 mt-4">
                        <h5>By Business Year (Loan Amount)</h5>
                        <ResponsiveContainer width="100%" height={300}>
                            <LineChart data={stats.by_year}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="business_year" />
                                <YAxis />
                                <Tooltip />
                                <Legend />
                                <Line type="monotone" dataKey="total_loan_amount" stroke="#ffc658" name="Loan Amount" />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default Dashboard;
