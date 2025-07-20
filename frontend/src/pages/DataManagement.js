import React, { useState } from 'react';
import axios from 'axios';
import { Modal, Button, Form, InputGroup, Col, Row } from 'react-bootstrap';

function DataManagement({ data, yearMonth, fetchData, onImportSuccess }) {
    const [file, setFile] = useState(null);
    const [importYear, setImportYear] = useState(new Date().getFullYear());
    const [importMonth, setImportMonth] = useState(new Date().getMonth() + 1);
    const [showEditModal, setShowEditModal] = useState(false);
    const [showHistoryModal, setShowHistoryModal] = useState(false);
    const [editingRow, setEditingRow] = useState(null);
    const [history, setHistory] = useState([]);

    const handleFileChange = (e) => {
        setFile(e.target.files[0]);
    };

    const handleImport = () => {
        const yearMonthForImport = `${importYear}-${String(importMonth).padStart(2, '0')}`;
        const formData = new FormData();
        formData.append('file', file);
        formData.append('year_month', yearMonthForImport);

        axios.post('/api/import', formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        }).then(() => {
            alert('File imported successfully');
            if(onImportSuccess) {
                onImportSuccess(yearMonthForImport);
            }
        }).catch(error => {
            console.error("Error importing file:", error);
            const errorMessage = error.response ? error.response.data.error : "An unknown error occurred";
            alert(`Error importing file: ${errorMessage}`);
        });
    };

    const handleExport = () => {
        window.location.href = `/api/export?year_month=${yearMonth}`;
    };

    const handleEdit = (row) => {
        setEditingRow(row);
        setShowEditModal(true);
    };

    const handleCloseEditModal = () => {
        setShowEditModal(false);
        setEditingRow(null);
    };

    const handleSave = () => {
        axios.put(`/api/data/${editingRow.id}`, editingRow)
            .then(() => {
                fetchData();
                handleCloseEditModal();
            })
            .catch(error => {
                console.error("Error updating data:", error);
                alert('Error updating data');
            });
    };

    const handleChange = (e) => {
        setEditingRow({ ...editingRow, [e.target.name]: e.target.value });
    };

    const handleShowHistory = (dataId) => {
        axios.get(`/api/history/${dataId}`)
            .then(response => {
                setHistory(response.data);
                setShowHistoryModal(true);
            })
            .catch(error => {
                console.error("Error fetching history:", error);
            });
    };

    const handleCloseHistoryModal = () => {
        setShowHistoryModal(false);
        setHistory([]);
    };

    const yearOptions = () => {
        const currentYear = new Date().getFullYear();
        const years = [];
        for (let i = currentYear + 1; i >= currentYear - 10; i--) {
            years.push(i);
        }
        return years.map(y => <option key={y} value={y}>{y}</option>);
    };

    const monthOptions = () => {
        return Array.from({length: 12}, (_, i) => i + 1).map(m => (
            <option key={m} value={m}>{m}</option>
        ));
    };

    return (
        <div className="card">
            <div className="card-header">
                <h3>Data Management</h3>
            </div>
            <div className="card-body">
                <div className="mb-3">
                    <Row className="align-items-end">
                        <Col md={5}>
                            <Form.Group>
                                <Form.Label>Import File</Form.Label>
                                <Form.Control type="file" onChange={handleFileChange} />
                            </Form.Group>
                        </Col>
                        <Col md={2}>
                            <Form.Group>
                                <Form.Label>Year</Form.Label>
                                <Form.Select value={importYear} onChange={e => setImportYear(e.target.value)}>
                                    {yearOptions()}
                                </Form.Select>
                            </Form.Group>
                        </Col>
                        <Col md={2}>
                            <Form.Group>
                                <Form.Label>Month</Form.Label>
                                <Form.Select value={importMonth} onChange={e => setImportMonth(e.target.value)}>
                                    {monthOptions()}
                                </Form.Select>
                            </Form.Group>
                        </Col>
                        <Col md={3} className="d-flex align-items-end">
                            <Button onClick={handleImport} disabled={!file} className="me-2">Import</Button>
                            <Button onClick={handleExport} variant="secondary">Export</Button>
                        </Col>
                    </Row>
                </div>
                <table className="table table-striped">
                    <thead>
                        <tr>
                            <th>序号</th>
                            <th>Company Name</th>
                            <th>Loan Amount</th>
                            <th>Guarantee Amount</th>
                            <th>Loan Status</th>
                            <th>Cooperation Bank</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {data.map((row, index) => (
                            <tr key={row.id}>
                                <td>{index + 1}</td>
                                <td>{row.company_name}</td>
                                <td>{row.loan_amount}</td>
                                <td>{row.guarantee_amount}</td>
                                <td>{row.loan_status}</td>
                                <td>{row.cooperation_bank}</td>
                                <td>
                                    <Button variant="primary" size="sm" onClick={() => handleEdit(row)}>Edit</Button>
                                    <Button variant="info" size="sm" className="ms-2" onClick={() => handleShowHistory(row.id)}>History</Button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {editingRow && (
                <Modal show={showEditModal} onHide={handleCloseEditModal}>
                    <Modal.Header closeButton>
                        <Modal.Title>Edit Data</Modal.Title>
                    </Modal.Header>
                    <Modal.Body>
                        <Form>
                            <Form.Group className="mb-3">
                                <Form.Label>Company Name</Form.Label>
                                <Form.Control type="text" name="company_name" value={editingRow.company_name} onChange={handleChange} />
                            </Form.Group>
                            {/* ... other form fields ... */}
                        </Form>
                    </Modal.Body>
                    <Modal.Footer>
                        <Button variant="secondary" onClick={handleCloseEditModal}>Close</Button>
                        <Button variant="primary" onClick={handleSave}>Save Changes</Button>
                    </Modal.Footer>
                </Modal>
            )}

            <Modal show={showHistoryModal} onHide={handleCloseHistoryModal} size="lg">
                <Modal.Header closeButton>
                    <Modal.Title>Change History</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    <table className="table">
                        <thead>
                            <tr>
                                <th>Changed At</th>
                                <th>Field</th>
                                <th>Old Value</th>
                                <th>New Value</th>
                                <th>Changed By</th>
                            </tr>
                        </thead>
                        <tbody>
                            {history.map(h => (
                                <tr key={h.id}>
                                    <td>{new Date(h.changed_at).toLocaleString()}</td>
                                    <td>{h.field_name}</td>
                                    <td>{h.old_value}</td>
                                    <td>{h.new_value}</td>
                                    <td>{h.changed_by}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </Modal.Body>
            </Modal>
        </div>
    );
}

export default DataManagement;