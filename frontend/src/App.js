import React from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import DataManagement from './pages/DataManagement';
import Dashboard from './pages/Dashboard';
import Comparison from './pages/Comparison';
import ImportDataPage from './pages/ImportDataPage';
import DataStatistics from './pages/DataStatistics';
import { DataProvider } from './DataContext';

import { Navbar, Nav, Container } from 'react-bootstrap';

function App() {
    return (
        <DataProvider>
            <Router>
                <div className="App">
                    <Navbar bg="dark" variant="dark" expand="lg">
                        <Container fluid>
                            <Navbar.Brand href="#home">业务数据管理</Navbar.Brand>
                            <Navbar.Toggle aria-controls="basic-navbar-nav" />
                            <Navbar.Collapse id="basic-navbar-nav">
                                <Nav className="me-auto">
                                    <Nav.Link as={Link} to="/dashboard">仪表盘</Nav.Link>
                                    <Nav.Link as={Link} to="/data-view">数据视图</Nav.Link>
                                    <Nav.Link as={Link} to="/data-statistics">数据统计</Nav.Link>
                                    <Nav.Link as={Link} to="/compare">对比分析</Nav.Link>
                                    <Nav.Link as={Link} to="/import-data">数据导入</Nav.Link>
                                </Nav>
                            </Navbar.Collapse>
                        </Container>
                    </Navbar>

                    <div className="container-fluid mt-4">
                        <Routes>
                            <Route path="/" element={<Dashboard />} />
                            <Route path="/dashboard" element={<Dashboard />} />
                            <Route path="/data-view" element={<DataManagement />} />
                            <Route path="/compare" element={<Comparison />} />
                            <Route path="/data-statistics" element={<DataStatistics />} />
                            <Route path="/import-data" element={<ImportDataPage />} />
                        </Routes>
                    </div>
                </div>
            </Router>
        </DataProvider>
    );
}

export default App;
