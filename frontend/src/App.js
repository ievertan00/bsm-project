import React, { useContext } from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';
import { BrowserRouter as Router, Route, Routes, Link, Navigate } from 'react-router-dom';
import { Form, Row, Col } from 'react-bootstrap'; // Import Row and Col from react-bootstrap
import DataManagement from './pages/DataManagement';
import Dashboard from './pages/Dashboard';
import Comparison from './pages/Comparison';
import ImportDataPage from './pages/ImportDataPage';
import { DataContext, DataProvider } from './DataContext';

function AppContent() {
    const { selectedYear, setSelectedYear, selectedMonth, setSelectedMonth, availableYears, availableMonths } = useContext(DataContext);

    const handleYearChange = (e) => {
        setSelectedYear(parseInt(e.target.value));
    };

    const handleMonthChange = (e) => {
        setSelectedMonth(parseInt(e.target.value));
    };

    // Filter available months based on selected year
    const monthsForSelectedYear = availableMonths
        .filter(m => m.year === selectedYear)
        .map(m => m.month)
        .sort((a, b) => a - b);

    const yearMonthsForComparison = availableMonths
        .map(item => `${item.year}-${String(item.month).padStart(2, '0')}`)
        .sort();

    return (
        <Router>
            <div className="App">
                <nav className="navbar navbar-expand-lg navbar-dark bg-dark">
                    <div className="container-fluid">
                        <Link className="navbar-brand" to="/dashboard">业务数据管理</Link>
                        <div className="collapse navbar-collapse" id="navbarNav">
                            <ul className="navbar-nav me-auto mb-2 mb-lg-0">
                                <li className="nav-item">
                                    <Link className="nav-link" to="/dashboard">仪表盘</Link>
                                </li>
                                <li className="nav-item">
                                    <Link className="nav-link" to="/data-view">数据视图</Link>
                                </li>
                                <li className="nav-item">
                                    <Link className="nav-link" to="/compare">对比分析</Link>
                                </li>
                                <li className="nav-item">
                                    <Link className="nav-link" to="/import-data">数据导入</Link>
                                </li>
                            </ul>
                            <Form className="d-flex">
                                <Row className="g-2 align-items-center">
                                    <Col xs="auto">
                                        <Form.Label className="text-light mb-0 me-2">年份:</Form.Label>
                                    </Col>
                                    <Col xs="auto">
                                        <Form.Control
                                            as="select"
                                            size="sm"
                                            value={selectedYear}
                                            onChange={handleYearChange}
                                            className="bg-secondary text-light border-0"
                                        >
                                            {availableYears.map(year => (
                                                <option key={year} value={year}>{year}年</option>
                                            ))}
                                        </Form.Control>
                                    </Col>
                                    <Col xs="auto">
                                        <Form.Label className="text-light mb-0 me-2">月份:</Form.Label>
                                    </Col>
                                    <Col xs="auto">
                                        <Form.Control
                                            as="select"
                                            size="sm"
                                            value={selectedMonth}
                                            onChange={handleMonthChange}
                                            className="bg-secondary text-light border-0"
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
                        </div>
                    </div>
                </nav>

                <div className="container-fluid mt-4">
                    <Routes>
                        <Route path="/" element={<Navigate to="/dashboard" />} />
                        <Route path="/dashboard" element={<Dashboard />} />
                        <Route path="/data-view" element={<DataManagement />} />
                        <Route path="/compare" element={<Comparison yearMonths={yearMonthsForComparison} />} />
                        <Route path="/import-data" element={<ImportDataPage />} />
                    </Routes>
                </div>
            </div>
        </Router>
    );
}

function App() {
    return (
        <DataProvider>
            <AppContent />
        </DataProvider>
    );
}

export default App;