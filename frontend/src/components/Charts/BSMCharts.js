import React from 'react';
import ReactECharts from 'echarts-for-react';

export const BalanceChart = ({ data, loading }) => {
  const option = {
    title: {
      text: 'Balance Over Time',
      left: 'center',
    },
    tooltip: {
      trigger: 'axis',
    },
    legend: {
      data: ['Outstanding Loan', 'Outstanding Guarantee'],
      bottom: 0,
    },
    xAxis: {
      type: 'category',
      data: data.map(item => item.period),
    },
    yAxis: {
      type: 'value',
      name: 'Amount (Million)',
    },
    series: [
      {
        name: 'Outstanding Loan',
        type: 'line',
        data: data.map(item => item.total_outstanding_loan),
        smooth: true,
        itemStyle: { color: '#1890ff' },
      },
      {
        name: 'Outstanding Guarantee',
        type: 'line',
        data: data.map(item => item.total_outstanding_guarantee),
        smooth: true,
        itemStyle: { color: '#52c41a' },
      },
    ],
  };

  return <ReactECharts option={option} showLoading={loading} style={{ height: '400px' }} />;
};

export const NewBusinessChart = ({ data, loading }) => {
  const option = {
    title: {
      text: 'New Business Over Time',
      left: 'center',
    },
    tooltip: {
      trigger: 'axis',
    },
    legend: {
      data: ['Loan Amount', 'Guarantee Amount'],
      bottom: 0,
    },
    xAxis: {
      type: 'category',
      data: data.map(item => item.period),
    },
    yAxis: {
      type: 'value',
      name: 'Amount (Million)',
    },
    series: [
      {
        name: 'Loan Amount',
        type: 'bar',
        data: data.map(item => item.total_loan),
        itemStyle: { color: '#40a9ff' },
      },
      {
        name: 'Guarantee Amount',
        type: 'bar',
        data: data.map(item => item.total_guarantee),
        itemStyle: { color: '#73d13d' },
      },
    ],
  };

  return <ReactECharts option={option} showLoading={loading} style={{ height: '400px' }} />;
};
