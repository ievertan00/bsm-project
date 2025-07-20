import React, { useState } from 'react';
import axios from 'axios';
import { Modal, Button, Form, Col, Row } from 'react-bootstrap';
import { Download, PencilSquare, ClockHistory, Trash } from 'react-bootstrap-icons';

function DataManagement({ data, yearMonth, fetchData }) {
    const [showEditModal, setShowEditModal] = useState(false);
    const [showHistoryModal, setShowHistoryModal] = useState(false);
    const [editingRow, setEditingRow] = useState(null);
    const [history, setHistory] = useState([]);

    const handleExport = () => {
        window.location.href = `/api/export?year_month=${yearMonth}`;
    };

    const handleEdit = (row) => {
        const formattedRow = {
            ...row,
            loan_start_date: row.loan_start_date ? new Date(row.loan_start_date).toISOString().split('T')[0] : '',
            loan_end_date: row.loan_end_date ? new Date(row.loan_end_date).toISOString().split('T')[0] : ''
        };
        setEditingRow(formattedRow);
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
        const { name, value, type } = e.target;
        const newValue = type === 'number' ? parseFloat(value) : value;
        setEditingRow({ ...editingRow, [name]: newValue });
    };

    const handleDelete = (dataId) => {
        if (window.confirm(`Are you sure you want to delete entry #${dataId}? This action cannot be undone.`)) {
            axios.delete(`/api/data/${dataId}`)
                .then(() => {
                    alert('Entry deleted successfully');
                    fetchData(); // Refresh the data view
                })
                .catch(error => {
                    console.error("Error deleting data:", error);
                    alert('Error deleting data');
                });
        }
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

    return (
        <div className="card">
            <div className="card-header d-flex justify-content-between align-items-center">
                <h3>Data View</h3>
                <Button onClick={handleExport} variant="secondary">
                    <Download /> Export Current View
                </Button>
            </div>
            <div className="card-body">
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
                                    <Button variant="primary" size="sm" onClick={() => handleEdit(row)}><PencilSquare /> Edit</Button>
                                    <Button variant="info" size="sm" className="ms-2" onClick={() => handleShowHistory(row.id)}><ClockHistory /> History</Button>
                                    <Button variant="danger" size="sm" className="ms-2" onClick={() => handleDelete(row.id)}><Trash /> Delete</Button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {editingRow && (
                <Modal show={showEditModal} onHide={handleCloseEditModal} size="lg">
                    <Modal.Header closeButton>
                        <Modal.Title>Edit Entry #{editingRow.id}</Modal.Title>
                    </Modal.Header>
                    <Modal.Body>
                        <Form>
                            <Row>
                                <Col md={6}>
                                    <Form.Group className="mb-3">
                                        <Form.Label>Company Name</Form.Label>
                                        <Form.Control type="text" name="company_name" value={editingRow.company_name || ''} onChange={handleChange} />
                                    </Form.Group>
                                </Col>
                                <Col md={6}>
                                    <Form.Group className="mb-3">
                                        <Form.Label>Cooperation Bank</Form.Label>
                                        <Form.Control type="text" name="cooperation_bank" value={editingRow.cooperation_bank || ''} onChange={handleChange} />
                                    </Form.Group>
                                </Col>
                            </Row>
                            <Row>
                                <Col md={6}>
                                    <Form.Group className="mb-3">
                                        <Form.Label>Loan Amount (万元)</Form.Label>
                                        <Form.Control type="number" name="loan_amount" value={editingRow.loan_amount || 0} onChange={handleChange} />
                                    </Form.Group>
                                </Col>
                                <Col md={6}>
                                    <Form.Group className="mb-3">
                                        <Form.Label>Guarantee Amount (万元)</Form.Label>
                                        <Form.Control type="number" name="guarantee_amount" value={editingRow.guarantee_amount || 0} onChange={handleChange} />
                                    </Form.Group>
                                </Col>
                            </Row>
                             <Row>
                                <Col md={6}>
                                    <Form.Group className="mb-3">
                                        <Form.Label>Loan Balance (万元)</Form.Label>
                                        <Form.Control type="number" name="loan_balance" value={editingRow.loan_balance || 0} onChange={handleChange} />
                                    </Form.Group>
                                </Col>
                                <Col md={6}>
                                    <Form.Group className="mb-3">
                                        <Form.Label>Guarantee Balance (万元)</Form.Label>
                                        <Form.Control type="number" name="guarantee_balance" value={editingRow.guarantee_balance || 0} onChange={handleChange} />
                                    </Form.Group>
                                </Col>
                            </Row>
                            <Row>
                                <Col md={6}>
                                    <Form.Group className="mb-3">
                                        <Form.Label>Loan Start Date</Form.Label>
                                        <Form.Control type="date" name="loan_start_date" value={editingRow.loan_start_date || ''} onChange={handleChange} />
                                    </Form.Group>
                                </Col>
                                <Col md={6}>
                                    <Form.Group className="mb-3">
                                        <Form.Label>Loan End Date</Form.Label>
                                        <Form.Control type="date" name="loan_end_date" value={editingRow.loan_end_date || ''} onChange={handleChange} />
                                    </Form.Group>
                                </Col>
                            </Row>
                            <Row>
                                <Col md={4}>
                                    <Form.Group className="mb-3">
                                        <Form.Label>Loan Status</Form.Label>
                                        <Form.Control type="text" name="loan_status" value={editingRow.loan_status || ''} onChange={handleChange} />
                                    </Form.Group>
                                </Col>
                                <Col md={4}>
                                    <Form.Group className="mb-3">
                                        <Form.Label>Business Type</Form.Label>
                                        <Form.Control type="text" name="business_type" value={editingRow.business_type || ''} onChange={handleChange} />
                                    </Form.Group>
                                </Col>
                                <Col md={4}>
                                    <Form.Group className="mb-3">
                                        <Form.Label>Business Year</Form.Label>
                                        <Form.Control type="number" name="business_year" value={editingRow.business_year || ''} onChange={handleChange} />
                                    </Form.Group>
                                </Col>
                            </Row>
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
