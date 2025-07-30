import React, { useState, useEffect, useContext } from 'react';
import axios from 'axios';
import { Card, Col, Row } from 'react-bootstrap';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { DataContext } from '../../DataContext';

const COLORS = ['#FAC795', '#FFE9BE', '#E3EDE0',  '#ABD3E1',  '#C59D94'];

function ChartsDisplay() {
    const { selectedYear, selectedMonth } = useContext(DataContext);
    const [chartData, setChartData] = useState(null);

    useEffect(() => {
        if (selectedYear && selectedMonth) {
            axios.get(`/api/charts-data?year=${selectedYear}&month=${selectedMonth}`)
                .then(response => {
                    setChartData(response.data);
                })
                .catch(error => {
                    console.error("Error fetching chart data:", error);
                });
        }
    }, [selectedYear, selectedMonth]);

    if (!chartData) {
        return null;
    }

    const { money_results, num_results } = chartData;

    const transformData = (moneyData, numData) => {
        const transformed = [];
        const years = Object.keys(moneyData).filter(y => y !== 'total');
        const businessTypes = ['常规业务', '建行批量业务', '微众批量业务', '工行批量业务'];

        businessTypes.forEach(type => {
            const entry = { name: type };
            years.forEach(year => {
                entry[`${year}_money`] = moneyData[year][type];
                entry[`${year}_num`] = numData[year][type];
            });
            transformed.push(entry);
        });
        
        // Add total entry
        const totalEntry = { name: '整体' };
        years.forEach(year => {
            totalEntry[`${year}_money`] = moneyData[year][businessTypes[0]] + moneyData[year][businessTypes[1]] + moneyData[year][businessTypes[2]] + moneyData[year][businessTypes[3]];
            totalEntry[`${year}_num`] = numData[year][businessTypes[0]] + numData[year][businessTypes[1]] + numData[year][businessTypes[2]] + numData[year][businessTypes[3]];
        });
        transformed.push(totalEntry);

        return transformed;
    };

    const combinedData = transformData(money_results, num_results);
    const years = Object.keys(money_results).filter(y => y !== 'total');

    return (
        <Card>
            <Card.Header>
                <h4>数据展示</h4>
            </Card.Header>
            <Card.Body>
                <Row>
                    <Col md={12} className="mb-4">
                        <h5>新增借款金额（万元）</h5>
                        <ResponsiveContainer width="100%" height={400}>
                            <BarChart data={combinedData}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="name" />
                                <YAxis />
                                <Tooltip formatter={(value) => `${value.toLocaleString()} 万元`} />
                                <Legend />
                                {years.map((year, index) => (
                                    <Bar key={`${year}_money`} dataKey={`${year}_money`} fill={COLORS[index % COLORS.length]} name={`${year}年`} />
                                ))}
                            </BarChart>
                        </ResponsiveContainer>
                    </Col>
                    <Col md={12} className="mb-4">
                        <h5>新增借款企业家数</h5>
                        <ResponsiveContainer width="100%" height={400}>
                            <BarChart data={combinedData}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="name" />
                                <YAxis />
                                <Tooltip formatter={(value) => `${value} 家`} />
                                <Legend />
                                {years.map((year, index) => (
                                    <Bar key={`${year}_num`} dataKey={`${year}_num`} fill={COLORS[index % COLORS.length]} name={`${year}年`} />
                                ))}
                            </BarChart>
                        </ResponsiveContainer>
                    </Col>
                </Row>
            </Card.Body>
        </Card>
    );
}

export default ChartsDisplay;