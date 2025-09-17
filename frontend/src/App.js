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

import { Navbar, Nav, Container, Button } from 'react-bootstrap';

function AppContent() {
    const { user, logout } = useContext(AuthContext);

    return (
        <Router>
            <div className="App">
                <Navbar bg="dark" variant="dark" expand="lg">
                    <Container fluid>
                        <Navbar.Brand href="#home">业务数据管理</Navbar.Brand>
                        <Navbar.Toggle aria-controls="basic-navbar-nav" />
                        <Navbar.Collapse id="basic-navbar-nav">
                            {user && (
                                <Nav className="me-auto">
                                    <Nav.Link as={Link} to="/dashboard">仪表盘</Nav.Link>
                                    <Nav.Link as={Link} to="/data-view">数据视图</Nav.Link>
                                    <Nav.Link as={Link} to="/data-statistics">数据统计</Nav.Link>
                                    <Nav.Link as={Link} to="/compare">对比分析</Nav.Link>
                                    <Nav.Link as={Link} to="/import-data">数据导入</Nav.Link>
                                </Nav>
                            )}
                            <div className="d-flex">
                                {user ? (
                                    <Button variant="outline-light" onClick={logout}>Logout</Button>
                                ) : (
                                    <Button as={Link} to="/login" variant="outline-light">Login</Button>
                                )}
                            </div>
                        </Navbar.Collapse>
                    </Container>
                </Navbar>

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
