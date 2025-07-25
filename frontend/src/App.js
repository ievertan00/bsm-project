import React from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';
import { BrowserRouter as Router, Route, Routes, Link, Navigate } from 'react-router-dom';
import DataManagement from './pages/DataManagement';
import Dashboard from './pages/Dashboard';
import Comparison from './pages/Comparison';
import ImportDataPage from './pages/ImportDataPage';
import DataStatistics from './pages/DataStatistics'; // Import the new page
import { DataProvider } from './DataContext';

function AppContent() {
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
                                    <Link className="nav-link" to="/data-statistics">数据统计</Link>
                                </li>
                                <li className="nav-item">
                                    <Link className="nav-link" to="/compare">对比分析</Link>
                                </li>

                                <li className="nav-item">
                                    <Link className="nav-link" to="/import-data">数据导入</Link>
                                </li>
                            </ul>
                        </div>
                    </div>
                </nav>

                <div className="container-fluid mt-4">
                    <Routes>
                        <Route path="/" element={<Navigate to="/dashboard" />} />
                        <Route path="/dashboard" element={<Dashboard />} />
                        <Route path="/data-view" element={<DataManagement />} />
                        <Route path="/compare" element={<Comparison />} />
                        <Route path="/data-statistics" element={<DataStatistics />} />
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