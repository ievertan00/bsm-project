import React, { useState } from 'react';
import axios from 'axios';
import { Button, Card, Col, Form, Row, ProgressBar, Tabs, Tab } from 'react-bootstrap';
import { Upload } from 'react-bootstrap-icons';

function ImportData({ onImportSuccess }) {
    // State for Single Import
    const [singleFile, setSingleFile] = useState(null);
    const [importYear, setImportYear] = useState(new Date().getFullYear());
    const [importMonth, setImportMonth] = useState(new Date().getMonth() + 1);

    // State for Bulk Import
    const [bulkFiles, setBulkFiles] = useState(null);
    const [progress, setProgress] = useState(0);
    const [isUploading, setIsUploading] = useState(false);

    // --- Single File Import Logic ---
    const handleSingleFileChange = (e) => {
        setSingleFile(e.target.files[0]);
    };

    const handleSingleImport = () => {
        const yearMonthForImport = `${importYear}-${String(importMonth).padStart(2, '0')}`;
        const formData = new FormData();
        formData.append('file', singleFile);
        formData.append('year_month', yearMonthForImport);

        axios.post('/api/import', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
            .then(() => {
                alert('File imported successfully');
                if(onImportSuccess) onImportSuccess(yearMonthForImport);
            })
            .catch(error => {
                console.error("Error importing file:", error);
                alert(`Error importing file: ${error.response?.data?.error || "Unknown error"}`);
            });
    };

    // --- Bulk Import Logic ---
    const handleBulkFileChange = (e) => {
        setBulkFiles(e.target.files);
    };

    const handleBulkImport = async () => {
        if (!bulkFiles || bulkFiles.length === 0) return alert("Please select files for bulk upload.");

        setIsUploading(true);
        setProgress(0);
        let lastImportedYearMonth = '';

        for (let i = 0; i < bulkFiles.length; i++) {
            const file = bulkFiles[i];
            const match = file.name.match(/(\d{4}-\d{2})/);
            if (!match) {
                alert(`Could not extract year-month from filename: ${file.name}. Skipping.`);
                setProgress(((i + 1) / bulkFiles.length) * 100);
                continue;
            }

            const yearMonth = match[1];
            const formData = new FormData();
            formData.append('file', file);
            formData.append('year_month', yearMonth);

            try {
                await axios.post('/api/import', formData, { headers: { 'Content-Type': 'multipart/form-data' } });
                lastImportedYearMonth = yearMonth;
            } catch (error) {
                console.error(`Error importing ${file.name}:`, error);
                alert(`Failed to import ${file.name}. Stopping bulk import.`);
                setIsUploading(false);
                return;
            }
            setProgress(((i + 1) / bulkFiles.length) * 100);
        }

        setIsUploading(false);
        alert("Bulk import completed successfully!");
        if (onImportSuccess && lastImportedYearMonth) onImportSuccess(lastImportedYearMonth);
    };

    // --- Helper Functions for UI ---
    const yearOptions = () => {
        const currentYear = new Date().getFullYear();
        const years = [];
        for (let i = currentYear + 1; i >= currentYear - 10; i--) years.push(i);
        return years.map(y => <option key={y} value={y}>{y}</option>);
    };

    const monthOptions = () => Array.from({length: 12}, (_, i) => i + 1).map(m => <option key={m} value={m}>{m}</option>);

    return (
        <Card className="mb-4">
            <Card.Header><h3>Import Data</h3></Card.Header>
            <Card.Body>
                <Tabs defaultActiveKey="single" id="import-tabs" className="mb-3">
                    <Tab eventKey="single" title="Single File Import">
                        <Row className="align-items-end pt-3">
                            <Col md={5}><Form.Group><Form.Label>Select Excel File</Form.Label><Form.Control type="file" onChange={handleSingleFileChange} /></Form.Group></Col>
                            <Col md={3}><Form.Group><Form.Label>Target Year</Form.Label><Form.Select value={importYear} onChange={e => setImportYear(e.target.value)}>{yearOptions()}</Form.Select></Form.Group></Col>
                            <Col md={2}><Form.Group><Form.Label>Target Month</Form.Label><Form.Select value={importMonth} onChange={e => setImportMonth(e.target.value)}>{monthOptions()}</Form.Select></Form.Group></Col>
                            <Col md={2} className="d-flex align-items-end"><Button onClick={handleSingleImport} disabled={!singleFile} className="w-100"><Upload /> Import</Button></Col>
                        </Row>
                    </Tab>
                    <Tab eventKey="bulk" title="Bulk Import">
                        <Row className="align-items-end pt-3">
                            <Col md={10}><Form.Group><Form.Label>Select Files (e.g., name_2025-01.xlsx)</Form.Label><Form.Control type="file" onChange={handleBulkFileChange} multiple /></Form.Group></Col>
                            <Col md={2} className="d-flex align-items-end"><Button onClick={handleBulkImport} disabled={!bulkFiles || isUploading} className="w-100"><Upload /> {isUploading ? 'Importing...' : 'Import'}</Button></Col>
                        </Row>
                        {isUploading && <ProgressBar animated now={progress} label={`${Math.round(progress)}%`} className="mt-3" />}
                    </Tab>
                </Tabs>
            </Card.Body>
        </Card>
    );
}

export default ImportData;
