import React from 'react';
import ImportData from '../components/ImportData'; // Import the original ImportData component
import { Card } from 'react-bootstrap';

function ImportDataPage() {
    // No need for onImportSuccess or onExport props here, as this is a standalone page
    // You might want to add some state or context if you need to refresh data elsewhere after import
    return (
        <Card>
            <Card.Header><h3>数据导入</h3></Card.Header>
            <Card.Body>
                <ImportData />
            </Card.Body>
        </Card>
    );
}

export default ImportDataPage;