import React, { useState, useEffect, useCallback, useContext } from 'react';
import axios from 'axios';
import { Modal, Button, Form, Col, Row, Table, Pagination, InputGroup } from 'react-bootstrap';
import { Download, PencilSquare, ClockHistory, Trash, Search } from 'react-bootstrap-icons';

import { DataContext } from '../DataContext'; // Import DataContext

function DataManagement() {
    const { selectedYear, selectedMonth } = useContext(DataContext); // Use context for year and month
    const [data, setData] = useState([]);
    const [showEditModal, setShowEditModal] = useState(false);
    const [showHistoryModal, setShowHistoryModal] = useState(false);
    const [editingRow, setEditingRow] = useState(null);
    const [history, setHistory] = useState([]);
    const [pagination, setPagination] = useState({ current_page: 1, pages: 1, total: 0 });
    const [searchTerm, setSearchTerm] = useState('');

    const fetchData = useCallback((page = 1, search = '') => {
        axios.get(`/api/data?page=${page}&per_page=15&company_name=${search}&year=${selectedYear}&month=${selectedMonth}`)
            .then(response => {
                setData(response.data.data);
                setPagination({
                    current_page: response.data.current_page,
                    pages: response.data.pages,
                    total: response.data.total
                });
            })
            .catch(error => {
                console.error("获取数据时出错:", error);
                alert('无法加载数据。');
            });
    }, [selectedYear, selectedMonth]); // Add selectedYear and selectedMonth to dependencies

    useEffect(() => {
        fetchData(1, searchTerm);
    }, [fetchData, searchTerm, selectedYear, selectedMonth]); // Add selectedYear and selectedMonth to dependencies

    const handlePageChange = (page) => {
        fetchData(page, searchTerm);
    };

    const handleSearch = () => {
        fetchData(1, searchTerm);
    };

    const handleExport = () => {
        window.location.href = '/api/export';
    };

    const handleEdit = (row) => {
        const formattedRow = Object.keys(row).reduce((acc, key) => {
            if (key.endsWith('_date') && row[key]) {
                acc[key] = new Date(row[key]).toISOString().split('T')[0];
            } else {
                acc[key] = row[key] === null ? '' : row[key];
            }
            return acc;
        }, {});
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
                fetchData(pagination.current_page, searchTerm);
                handleCloseEditModal();
            })
            .catch(error => {
                console.error("更新数据时出错:", error);
                alert('更新数据失败。');
            });
    };

    const handleChange = (e) => {
        const { name, value, type, checked } = e.target;
        const val = type === 'checkbox' ? checked : (type === 'number' ? parseFloat(value) : value);
        setEditingRow({ ...editingRow, [name]: val });
    };

    const handleDelete = (dataId) => {
        if (window.confirm(`您确定要删除ID为 ${dataId} 的条目吗？此操作无法撤销。`)) {
            axios.delete(`/api/data/${dataId}`)
                .then(() => {
                    alert('条目已成功删除。');
                    fetchData(pagination.current_page, searchTerm);
                })
                .catch(error => {
                    console.error("删除数据时出错:", error);
                    alert('删除数据失败。');
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
                console.error("获取历史记录时出错:", error);
            });
    };

    const handleCloseHistoryModal = () => {
        setShowHistoryModal(false);
        setHistory([]);
    };

    

    const renderPagination = () => {
        let items = [];
        for (let number = 1; number <= pagination.pages; number++) {
            items.push(
                <Pagination.Item key={number} active={number === pagination.current_page} onClick={() => handlePageChange(number)}>
                    {number}
                </Pagination.Item>,
            );
        }
        return <Pagination>{items}</Pagination>;
    };

    return (
        <div className="card">
            <div className="card-header d-flex justify-content-between align-items-center">
                <h3>数据视图 - {selectedYear}年{selectedMonth}月</h3>
            </div>
            <div className="card-body">
                <Row className="mb-3">
                    <Col md={12}>
                        {/* Other potential controls or empty space */}
                    </Col>
                </Row>
                <InputGroup className="mb-3 mt-3">
                    <Form.Control
                        placeholder="按企业名称搜索..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        onKeyPress={event => event.key === 'Enter' && handleSearch()}
                    />
                    <Button variant="outline-secondary" onClick={handleSearch}><Search /></Button>
                </InputGroup>

                <div style={{ overflowX: 'auto' }}>
                    <Table striped bordered hover responsive>
                        <thead>
                            <tr>
                                <th style={{ whiteSpace: 'nowrap' }}>序号</th>
                                <th style={{ whiteSpace: 'nowrap' }}>企业名称</th>
                                <th style={{ whiteSpace: 'nowrap' }}>借款金额（万元）</th>
                                <th style={{ whiteSpace: 'nowrap' }}>担保金额（万元）</th>
                                <th style={{ whiteSpace: 'nowrap' }}>借款起始日</th>
                                <th style={{ whiteSpace: 'nowrap' }}>借款到期日</th>
                                <th style={{ whiteSpace: 'nowrap' }}>借款利率</th>
                                <th style={{ whiteSpace: 'nowrap' }}>担保费率</th>
                                <th style={{ whiteSpace: 'nowrap' }}>借款余额（万元）</th>
                                <th style={{ whiteSpace: 'nowrap' }}>担保余额（万元）</th>
                                <th style={{ whiteSpace: 'nowrap' }}>借据状态</th>
                                <th style={{ whiteSpace: 'nowrap' }}>结清日期</th>
                                <th style={{ whiteSpace: 'nowrap' }}>企业划型</th>
                                <th style={{ whiteSpace: 'nowrap' }}>合作银行</th>
                                <th style={{ whiteSpace: 'nowrap' }}>业务年度</th>
                                <th style={{ whiteSpace: 'nowrap' }}>业务类型</th>
                                <th style={{ whiteSpace: 'nowrap' }}>企业规模</th>
                                <th style={{ whiteSpace: 'nowrap' }}>成立日期</th>
                                <th style={{ whiteSpace: 'nowrap' }}>注册资本</th>
                                <th style={{ whiteSpace: 'nowrap' }}>企业（机构）类型</th>
                                <th style={{ whiteSpace: 'nowrap' }}>国标行业门类</th>
                                <th style={{ whiteSpace: 'nowrap' }}>国标行业大类</th>
                                <th style={{ whiteSpace: 'nowrap' }}>企查查行业门类</th>
                                <th style={{ whiteSpace: 'nowrap' }}>企查查行业大类</th>
                                <th style={{ whiteSpace: 'nowrap' }}>专精特新“小巨人”企业</th>
                                <th style={{ whiteSpace: 'nowrap' }}>专精特新中小企业</th>
                                <th style={{ whiteSpace: 'nowrap' }}>高新技术企业</th>
                                <th style={{ whiteSpace: 'nowrap' }}>创新型中小企业</th>
                                <th style={{ whiteSpace: 'nowrap' }}>科技型中小企业</th>
                                <th style={{ whiteSpace: 'nowrap' }}>科技企业</th>
                                <th style={{ whiteSpace: 'nowrap' }}>操作</th>
                            </tr>
                        </thead>
                        <tbody>
                            {data.map((row, index) => (
                                <tr key={row.id}>
                                    <td style={{ whiteSpace: 'nowrap' }}>{(pagination.current_page - 1) * 15 + index + 1}</td>
                                    <td style={{ whiteSpace: 'nowrap' }}>{row.company_name}</td>
                                    <td style={{ whiteSpace: 'nowrap' }}>{row.loan_amount}</td>
                                    <td style={{ whiteSpace: 'nowrap' }}>{row.guarantee_amount}</td>
                                    <td style={{ whiteSpace: 'nowrap' }}>{row.loan_start_date}</td>
                                    <td style={{ whiteSpace: 'nowrap' }}>{row.loan_due_date}</td>
                                    <td style={{ whiteSpace: 'nowrap' }}>{row.loan_interest_rate}</td>
                                    <td style={{ whiteSpace: 'nowrap' }}>{row.guarantee_fee_rate}</td>
                                    <td style={{ whiteSpace: 'nowrap' }}>{row.outstanding_loan_balance}</td>
                                    <td style={{ whiteSpace: 'nowrap' }}>{row.outstanding_guarantee_balance}</td>
                                    <td style={{ whiteSpace: 'nowrap' }}>{row.loan_status}</td>
                                    <td style={{ whiteSpace: 'nowrap' }}>{row.settlement_date}</td>
                                    <td style={{ whiteSpace: 'nowrap' }}>{row.enterprise_classification}</td>
                                    <td style={{ whiteSpace: 'nowrap' }}>{row.cooperative_bank}</td>
                                    <td style={{ whiteSpace: 'nowrap' }}>{row.business_year}</td>
                                    <td style={{ whiteSpace: 'nowrap' }}>{row.business_type}</td>
                                    <td style={{ whiteSpace: 'nowrap' }}>{row.enterprise_size}</td>
                                    <td style={{ whiteSpace: 'nowrap' }}>{row.establishment_date}</td>
                                    <td style={{ whiteSpace: 'nowrap' }}>{row.registered_capital}</td>
                                    <td style={{ whiteSpace: 'nowrap' }}>{row.enterprise_institution_type}</td>
                                    <td style={{ whiteSpace: 'nowrap' }}>{row.national_standard_industry_category_main}</td>
                                    <td style={{ whiteSpace: 'nowrap' }}>{row.national_standard_industry_category_major}</td>
                                    <td style={{ whiteSpace: 'nowrap' }}>{row.qichacha_industry_category_main}</td>
                                    <td style={{ whiteSpace: 'nowrap' }}>{row.qichacha_industry_category_major}</td>
                                    <td style={{ whiteSpace: 'nowrap' }}>{row.is_little_giant_enterprise ? '是' : '否'}</td>
                                    <td style={{ whiteSpace: 'nowrap' }}>{row.is_srun_sme ? '是' : '否'}</td>
                                    <td style={{ whiteSpace: 'nowrap' }}>{row.is_high_tech_enterprise ? '是' : '否'}</td>
                                    <td style={{ whiteSpace: 'nowrap' }}>{row.is_innovative_sme ? '是' : '否'}</td>
                                    <td style={{ whiteSpace: 'nowrap' }}>{row.is_tech_based_sme ? '是' : '否'}</td>
                                    <td style={{ whiteSpace: 'nowrap' }}>{row.is_technology_enterprise ? '是' : '否'}</td>
                                    <td style={{ whiteSpace: 'nowrap' }}>
                                        <Button variant="primary" size="sm" onClick={() => handleEdit(row)}><PencilSquare /> 编辑</Button>
                                        <Button variant="info" size="sm" className="ms-2" onClick={() => handleShowHistory(row.id)}><ClockHistory /> 历史</Button>
                                        <Button variant="danger" size="sm" className="ms-2" onClick={() => handleDelete(row.id)}><Trash /> 删除</Button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </Table>
                </div>
                <div className="d-flex justify-content-center">
                    {renderPagination()}
                </div>
            </div>

            {editingRow && (
                <Modal show={showEditModal} onHide={handleCloseEditModal} size="xl">
                    <Modal.Header closeButton>
                        <Modal.Title>编辑条目 #{editingRow.id}</Modal.Title>
                    </Modal.Header>
                    <Modal.Body>
                        <Form>
                            {/* Render all fields from the new model */}
                            <Row>
                                {Object.keys(editingRow).map(key => {
                                    if (key === 'id' || key === 'created_at') return null;
                                    const type = typeof editingRow[key] === 'boolean' ? 'checkbox' : (key.includes('_date') ? 'date' : (typeof editingRow[key] === 'number' ? 'number' : 'text'));
                                    return (
                                        <Col md={4} key={key}>
                                            <Form.Group className="mb-3">
                                                <Form.Label>{key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</Form.Label>
                                                <Form.Control 
                                                    type={type} 
                                                    name={key} 
                                                    checked={type === 'checkbox' ? editingRow[key] : undefined}
                                                    value={type !== 'checkbox' ? editingRow[key] : undefined}
                                                    onChange={handleChange} 
                                                />
                                            </Form.Group>
                                        </Col>
                                    );
                                })}
                            </Row>
                        </Form>
                    </Modal.Body>
                    <Modal.Footer>
                        <Button variant="secondary" onClick={handleCloseEditModal}>关闭</Button>
                        <Button variant="primary" onClick={handleSave}>保存更改</Button>
                    </Modal.Footer>
                </Modal>
            )}

            <Modal show={showHistoryModal} onHide={handleCloseHistoryModal} size="lg">
                <Modal.Header closeButton>
                    <Modal.Title>变更历史</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    <Table striped bordered hover responsive>
                        <thead>
                            <tr>
                                <th>变更时间</th>
                                <th>字段</th>
                                <th>旧值</th>
                                <th>新值</th>
                                <th>变更人</th>
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
                    </Table>
                </Modal.Body>
            </Modal>
        </div>
    );
}

export default DataManagement;