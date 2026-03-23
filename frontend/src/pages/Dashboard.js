import React, { useState, useEffect } from 'react';
import { Row, Col, Card, Statistic, Spin, message } from 'antd';
import { 
  BankOutlined, 
  SafetyCertificateOutlined, 
  TeamOutlined, 
  ArrowUpOutlined 
} from '@ant-design/icons';
import axiosInstance from '../api/axiosConfig';
import { BalanceChart, NewBusinessChart } from '../components/Charts/BSMCharts';

const Dashboard = () => {
  const [summary, setSummary] = useState(null);
  const [trends, setTrends] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [summaryRes, trendsRes] = await Promise.all([
          axiosInstance.get('/dashboard/summary'),
          axiosInstance.get('/dashboard/growth')
        ]);
        setSummary(summaryRes.data);
        setTrends(trendsRes.data);
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
        message.error('Failed to load dashboard data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading && !summary) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '80vh' }}>
        <Spin size="large" tip="Loading Dashboard..." />
      </div>
    );
  }

  return (
    <div style={{ padding: '24px' }}>
      <h2 style={{ marginBottom: '24px' }}>Business Data Dashboard</h2>
      
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} lg={6}>
          <Card bordered={false}>
            <Statistic
              title="Total Companies"
              value={summary?.total_companies}
              prefix={<TeamOutlined />}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card bordered={false}>
            <Statistic
              title="Total Loan Amount"
              value={summary?.total_loan}
              precision={2}
              prefix={<BankOutlined />}
              suffix="M"
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card bordered={false}>
            <Statistic
              title="Total Guarantee Amount"
              value={summary?.total_guarantee}
              precision={2}
              prefix={<SafetyCertificateOutlined />}
              suffix="M"
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card bordered={false}>
            <Statistic
              title="Current Loan Balance"
              value={summary?.total_outstanding_loan}
              precision={2}
              prefix={<ArrowUpOutlined />}
              suffix="M"
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: '24px' }}>
        <Col span={24} lg={12}>
          <Card title="Balance Trends" bordered={false}>
            <BalanceChart data={trends} loading={loading} />
          </Card>
        </Col>
        <Col span={24} lg={12}>
          <Card title="New Business Trends" bordered={false}>
            <NewBusinessChart data={trends} loading={loading} />
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;
