import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import 'bootstrap/dist/css/bootstrap.min.css';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import DataManagement from './pages/DataManagement';
import Dashboard from './pages/Dashboard';
import Comparison from './pages/Comparison';

function App() {
    const [yearMonths, setYearMonths] = useState([]);
    const [yearMonth, setYearMonth] = useState('');
    const [data, setData] = useState([]);

    const fetchYearMonths = useCallback((selectYearMonth) => {
        axios.get('/api/year_months')
            .then(response => {
                const fetchedYearMonths = response.data.sort().reverse();
                setYearMonths(fetchedYearMonths);
                if (selectYearMonth) {
                    setYearMonth(selectYearMonth);
                } else if (fetchedYearMonths.length > 0 && !yearMonth) {
                    setYearMonth(fetchedYearMonths[0]);
                }
            })
            .catch(error => {
                console.error("Error fetching year months:", error);
            });
    }, [yearMonth]);

    useEffect(() => {
        fetchYearMonths();
    }, []);

    useEffect(() => {
        if (yearMonth) {
            fetchData();
        }
    }, [yearMonth]);

    const fetchData = () => {
        axios.get(`/api/data?year_month=${yearMonth}`)
            .then(response => {
                setData(response.data);
            })
            .catch(error => {
                console.error("Error fetching data:", error);
                setData([]); // Clear data on error
            });
    };

    const handleImportSuccess = (newYearMonth) => {
        fetchYearMonths(newYearMonth);
    };

    return (
        <Router>
            <div className="App">
                <nav className="navbar navbar-expand-lg navbar-dark bg-dark">
                    <div className="container-fluid">
                        <Link className="navbar-brand" to="/">Business Data Management</Link>
                        <div className="collapse navbar-collapse">
                            <ul className="navbar-nav me-auto mb-2 mb-lg-0">
                                <li className="nav-item">
                                    <Link className="nav-link" to="/compare">Compare</Link>
                                </li>
                            </ul>
                            <form className="d-flex">
                                <select className="form-select me-2" value={yearMonth} onChange={(e) => setYearMonth(e.target.value)}>
                                    {yearMonths.map(ym => (
                                        <option key={ym} value={ym}>{ym}</option>
                                    ))}
                                </select>
                            </form>
                        </div>
                    </div>
                </nav>

                <div className="container-fluid mt-4">
                    <Routes>
                        <Route path="/" element={
                            <>
                                <DataManagement 
                                    data={data} 
                                    yearMonth={yearMonth} 
                                    fetchData={fetchData} 
                                    onImportSuccess={handleImportSuccess} 
                                />
                                <Dashboard yearMonth={yearMonth} />
                            </>
                        } />
                        <Route path="/compare" element={<Comparison yearMonths={yearMonths} />} />
                    </Routes>
                </div>
            </div>
        </Router>
    );
}

export default App;