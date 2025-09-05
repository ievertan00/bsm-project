import React from 'react';
import ImportData from '../components/ImportData'; // Import the original ImportData component
import { Card } from 'react-bootstrap';

function ImportDataPage() {
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