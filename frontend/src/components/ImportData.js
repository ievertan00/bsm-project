import React, { useState, useEffect, useContext } from 'react';
import api from '../api';
import { Button, Form, Alert, Row, Col, Card, Nav, Tab, TabContainer } from 'react-bootstrap'; // Added TabContainer
import { Upload } from 'react-bootstrap-icons';
import { DataContext } from '../DataContext';

function ImportData({ onImportSuccess }) {
    const { refreshAvailableDates } = useContext(DataContext);
    // State to manage active tab
    const [activeKey, setActiveKey] = useState('singleImport'); // Added activeKey state

    // Single file import states
    const [singleFile, setSingleFile] = useState(null);
    const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());
    const [selectedMonth, setSelectedMonth] = useState(new Date().getMonth() + 1);
    const [isSingleUploading, setIsSingleUploading] = useState(false);
    const [singleError, setSingleError] = useState('');
    const [singleSuccess, setSingleSuccess] = useState('');

    // Batch file import states
    const [batchFiles, setBatchFiles] = useState([]);
    const [isBatchUploading, setIsBatchUploading] = useState(false);
    const [batchResults, setBatchResults] = useState([]); // Stores detailed results
    const [batchSummaryMessage, setBatchSummaryMessage] = useState(''); // Stores the consolidated message
    const [batchSummaryVariant, setBatchSummaryVariant] = useState('info'); // Variant for the summary alert

    // QCC Industry import states
    const [qccIndustryFile, setQccIndustryFile] = useState(null);
    const [isQccIndustryUploading, setIsQccIndustryUploading] = useState(false);
    const [qccIndustryError, setQccIndustryError] = useState('');
    const [qccIndustrySuccess, setQccIndustrySuccess] = useState('');

    // QCC Tech import states
    const [qccTechFile, setQccTechFile] = useState(null);
    const [isQccTechUploading, setIsQccTechUploading] = useState(false);
    const [qccTechError, setQccTechError] = useState('');
    const [qccTechSuccess, setQccTechSuccess] = useState('');

    const years = Array.from({ length: 20 }, (_, i) => new Date().getFullYear() - 5 + i); // Current year +/- 2
    const months = Array.from({ length: 12 }, (_, i) => i + 1);

    // Effect to clear batch results after a delay
    useEffect(() => {
        if (batchSummaryMessage) {
            const timer = setTimeout(() => {
                setBatchSummaryMessage('');
                setBatchResults([]); // Clear detailed results too
            }, 5000); // Clear after 5 seconds
            return () => clearTimeout(timer);
        }
    }, [batchSummaryMessage]);

    const handleSingleFileChange = (e) => {
        setSingleFile(e.target.files[0]);
        setSingleError('');
        setSingleSuccess('');
    };

    const handleQccIndustryFileChange = (e) => {
        setQccIndustryFile(e.target.files[0]);
        setQccIndustryError('');
        setQccIndustrySuccess('');
    };

    const handleQccTechFileChange = (e) => {
        setQccTechFile(e.target.files[0]);
        setQccTechError('');
        setQccTechSuccess('');
    };

    const handleSingleImport = () => {
        if (!singleFile) {
            setSingleError('请先选择一个文件。');
            return;
        }

        const formData = new FormData();
        formData.append('file', singleFile);
        formData.append('year', selectedYear);
        formData.append('month', selectedMonth);

        setIsSingleUploading(true);
        setSingleError('');
        setSingleSuccess('');

        api.post('/api/import', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        })
        .then(() => {
            setSingleSuccess(`数据导入成功！${selectedYear}年${selectedMonth}月的数据已更新。表格将刷新。`);
            if(onImportSuccess) onImportSuccess();
            setSingleFile(null); // Clear file input
            // Optionally reset year/month to current
            setSelectedYear(new Date().getFullYear());
            setSelectedMonth(new Date().getMonth() + 1);
            refreshAvailableDates(); // Refresh available dates in context
        })
        .catch(err => {
            const errorMessage = err.response?.data?.error || "未知错误";
            setSingleError(`导入失败: ${errorMessage}`);
            console.error("导入文件时出错:", err);
        })
        .finally(() => {
            setIsSingleUploading(false);
        });
    };

    const handleQccIndustryImport = () => {
        if (!qccIndustryFile) {
            setQccIndustryError('请先选择一个文件。');
            return;
        }

        const formData = new FormData();
        formData.append('file', qccIndustryFile);

        setIsQccIndustryUploading(true);
        setQccIndustryError('');
        setQccIndustrySuccess('');

        api.post('/api/import/qcc-industry', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        })
        .then(() => {
            setQccIndustrySuccess('QCC Industry data imported successfully.');
            setQccIndustryFile(null);
        })
        .catch(err => {
            const errorMessage = err.response?.data?.error || "Unknown error";
            setQccIndustryError(`Import failed: ${errorMessage}`);
        })
        .finally(() => {
            setIsQccIndustryUploading(false);
        });
    };

    const handleQccTechImport = () => {
        if (!qccTechFile) {
            setQccTechError('请先选择一个文件。');
            return;
        }

        const formData = new FormData();
        formData.append('file', qccTechFile);

        setIsQccTechUploading(true);
        setQccTechError('');
        setQccTechSuccess('');

        api.post('/api/import/qcc-tech', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        })
        .then(() => {
            setQccTechSuccess('QCC Tech data imported successfully.');
            setQccTechFile(null);
        })
        .catch(err => {
            const errorMessage = err.response?.data?.error || "Unknown error";
            setQccTechError(`Import failed: ${errorMessage}`);
        })
        .finally(() => {
            setIsQccTechUploading(false);
        });
    };

    const handleBatchFileChange = (e) => {
        setBatchFiles(Array.from(e.target.files));
        setBatchResults([]);
        setBatchSummaryMessage(''); // Clear previous summary
    };

    const handleBatchImport = async () => {
        if (batchFiles.length === 0) {
            setBatchSummaryMessage('请先选择文件进行批量导入。');
            setBatchSummaryVariant('danger');
            return;
        }

        setIsBatchUploading(true);
        setBatchResults([]);
        setBatchSummaryMessage('');
        const formData = new FormData();
        for (const file of batchFiles) {
            formData.append('files[]', file); // Use a consistent key for all files
        }

        try {
            const response = await api.post('/api/import', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            
            const results = response.data.results || [];
            setBatchResults(results);

            const successCount = results.filter(r => r.status === 'success').length;
            const failedCount = results.filter(r => r.status === 'failed').length;

            if (failedCount === 0) {
                setBatchSummaryMessage(`批量导入完成：所有 ${successCount} 个文件均成功导入！`);
                setBatchSummaryVariant('success');
                if (onImportSuccess) onImportSuccess();
            } else if (successCount === 0) {
                setBatchSummaryMessage(`批量导入失败：所有 ${failedCount} 个文件均导入失败。`);
                setBatchSummaryVariant('danger');
            } else {
                setBatchSummaryMessage(`批量导入完成：成功 ${successCount} 个文件，失败 ${failedCount} 个文件。`);
                setBatchSummaryVariant('warning');
                if (onImportSuccess) onImportSuccess(); // Still refresh if some succeeded
            }
            refreshAvailableDates(); // Refresh available dates in context

        } catch (err) {
            const errorMessage = err.response?.data?.error || "未知错误";
            setBatchSummaryMessage(`批量导入请求失败: ${errorMessage}`);
            setBatchSummaryVariant('danger');
console.error("批量导入文件时出错:", err);
        }
        finally {
            setIsBatchUploading(false);
        }
    };

    return (
        <Card className="mb-4">
            <Card.Header>
                <TabContainer activeKey={activeKey} onSelect={(k) => setActiveKey(k)}>
                    <Nav variant="tabs">
                        <Nav.Item>
                            <Nav.Link eventKey="singleImport">导入单月Excel数据</Nav.Link>
                        </Nav.Item>
                        <Nav.Item>
                            <Nav.Link eventKey="batchImport">批量导入Excel数据</Nav.Link>
                        </Nav.Item>
                        <Nav.Item>
                            <Nav.Link eventKey="qccIndustryImport">Import QCC Industry</Nav.Link>
                        </Nav.Item>
                        <Nav.Item>
                            <Nav.Link eventKey="qccTechImport">Import QCC Tech</Nav.Link>
                        </Nav.Item>
                    </Nav>
                    <Card.Body>
                        <Tab.Content>
                            <Tab.Pane eventKey="singleImport" className="py-3">
                                <Form.Group className="mb-3">
                                    <Form.Label>选择文件</Form.Label>
                                    <Form.Control type="file" onChange={handleSingleFileChange} accept=".xlsx, .xls" />
                                    <Form.Text className="text-muted">
                                        选择一个Excel文件进行导入。
                                    </Form.Text>
                                </Form.Group>

                                <Row className="mb-3">
                                    <Col>
                                        <Form.Group>
                                            <Form.Label>选择年份</Form.Label>
                                            <Form.Control as="select" value={selectedYear} onChange={e => setSelectedYear(parseInt(e.target.value))}>
                                                {years.map(year => <option key={year} value={year}>{year}年</option>)}
                                            </Form.Control>
                                        </Form.Group>
                                    </Col>
                                    <Col>
                                        <Form.Group>
                                            <Form.Label>选择月份</Form.Label>
                                            <Form.Control as="select" value={selectedMonth} onChange={e => setSelectedMonth(parseInt(e.target.value))}>
                                                {months.map(month => <option key={month} value={month}>{month}月</option>)}
                                            </Form.Control>
                                        </Form.Group>
                                    </Col>
                                </Row>
                                <Form.Text className="text-muted mb-3 d-block">
                                    导入的数据将覆盖所选年月的现有数据。
                                </Form.Text>
                                <Button onClick={handleSingleImport} disabled={!singleFile || isSingleUploading} className="mt-3">
                                    <Upload /> {isSingleUploading ? '正在导入...' : '导入并覆盖'}
                                </Button>
                                {singleError && <Alert variant="danger" className="mt-2">{singleError}</Alert>}
                                {singleSuccess && <Alert variant="success" className="mt-2">{singleSuccess}</Alert>}
                            </Tab.Pane>
                            <Tab.Pane eventKey="batchImport" className="py-3">
                                <Form.Group className="mb-3">
                                    <Form.Label>选择多个文件</Form.Label>
                                    <Form.Control type="file" multiple onChange={handleBatchFileChange} accept=".xlsx, .xls" />
                                    <Form.Text className="text-muted">
                                        选择多个Excel文件进行批量导入。文件名必须为 `sample_data_YYYY-MM.xlsx` 格式，数据将覆盖对应年月的现有数据。
                                    </Form.Text>
                                </Form.Group>
                                <Button onClick={handleBatchImport} disabled={batchFiles.length === 0 || isBatchUploading} className="mt-3">
                                    <Upload /> {isBatchUploading ? '正在批量导入...' : '批量导入并覆盖'}
                                </Button>
                                {batchSummaryMessage && <Alert variant={batchSummaryVariant} className="mt-3">{batchSummaryMessage}</Alert>}
                                {batchResults.length > 0 && batchSummaryVariant === 'warning' && (
                                    <div className="mt-2">
                                        <h6>失败文件详情:</h6>
                                        <ul>
                                            {batchResults.filter(r => r.status === 'failed').map((result, index) => (
                                                <li key={index} className="text-danger"><strong>{result.filename}:</strong> {result.message}</li>
                                            ))}
                                        </ul>
                                    </div>
                                )}
                            </Tab.Pane>
                            <Tab.Pane eventKey="qccIndustryImport" className="py-3">
                                <Form.Group className="mb-3">
                                    <Form.Label>Select QCC Industry File</Form.Label>
                                    <Form.Control type="file" onChange={handleQccIndustryFileChange} accept=".xlsx, .xls" />
                                    <Form.Text className="text-muted">
                                        Select an Excel file to import QCC Industry data. This will overwrite all existing QCC Industry data.
                                    </Form.Text>
                                </Form.Group>
                                <Button onClick={handleQccIndustryImport} disabled={!qccIndustryFile || isQccIndustryUploading} className="mt-3">
                                    <Upload /> {isQccIndustryUploading ? 'Importing...' : 'Import and Overwrite'}
                                </Button>
                                {qccIndustryError && <Alert variant="danger" className="mt-2">{qccIndustryError}</Alert>}
                                {qccIndustrySuccess && <Alert variant="success" className="mt-2">{qccIndustrySuccess}</Alert>}
                            </Tab.Pane>
                            <Tab.Pane eventKey="qccTechImport" className="py-3">
                                <Form.Group className="mb-3">
                                    <Form.Label>Select QCC Tech File</Form.Label>
                                    <Form.Control type="file" onChange={handleQccTechFileChange} accept=".csv" />
                                    <Form.Text className="text-muted">
                                        Select a CSV file to import QCC Tech data. This will overwrite all existing QCC Tech data.
                                    </Form.Text>
                                </Form.Group>
                                <Button onClick={handleQccTechImport} disabled={!qccTechFile || isQccTechUploading} className="mt-3">
                                    <Upload /> {isQccTechUploading ? 'Importing...' : 'Import and Overwrite'}
                                </Button>
                                {qccTechError && <Alert variant="danger" className="mt-2">{qccTechError}</Alert>}
                                {qccTechSuccess && <Alert variant="success" className="mt-2">{qccTechSuccess}</Alert>}
                            </Tab.Pane>
                        </Tab.Content>
                    </Card.Body>
                </TabContainer>
            </Card.Header>
        </Card>
    );
}

export default ImportData;
