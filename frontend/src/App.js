import React, { useContext } from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';
import { BrowserRouter as Router, Route, Routes, Link, Navigate } from 'react-router-dom';
import DataManagement from './pages/DataManagement';
import Dashboard from './pages/Dashboard';
import Comparison from './pages/Comparison';
import ImportDataPage from './pages/ImportDataPage';
import DataStatistics from './pages/DataStatistics';
import LoginPage from './pages/LoginPage';
import { DataProvider } from './DataContext';
import { AuthProvider, AuthContext } from './AuthContext';

function AppContent() {
    const { user, logout } = useContext(AuthContext);

    return (
        <Router>
            <div className="App">
                <nav className="navbar navbar-expand-lg navbar-dark bg-dark">
                    <div className="container-fluid">
                        <div className="navbar-brand">业务数据管理</div>
                        <div className="collapse navbar-collapse" id="navbarNav">
                            {user ? (
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
                            ) : null}
                        </div>
                        <div className="d-flex">
                            {user ? (
                                <button className="btn btn-outline-light" onClick={logout}>Logout</button>
                            ) : (
                                <>
                                    <Link className="btn btn-outline-light me-2" to="/login">Login</Link>
                                </>
                            )}
                        </div>
                    </div>
                </nav>

                <div className="container-fluid mt-4">
                    <Routes>
                        <Route path="/" element={user ? <Navigate to="/dashboard" /> : <Navigate to="/login" />} />
                        <Route path="/dashboard" element={user ? <Dashboard /> : <Navigate to="/login" />} />
                        <Route path="/data-view" element={user ? <DataManagement /> : <Navigate to="/login" />} />
                        <Route path="/compare" element={user ? <Comparison /> : <Navigate to="/login" />} />
                        <Route path="/data-statistics" element={user ? <DataStatistics /> : <Navigate to="/login" />} />
                        <Route path="/import-data" element={user ? <ImportDataPage /> : <Navigate to="/login" />} />
                        <Route path="/login" element={<LoginPage />} />
                    </Routes>
                </div>
            </div>
        </Router>
    );
}

function App() {
    return (
        <AuthProvider>
            <DataProvider>
                <AppContent />
            </DataProvider>
        </AuthProvider>
    );
}

export default App;
