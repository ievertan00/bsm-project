import React, { useState } from 'react';
import api from '../api';
import { useNavigate } from 'react-router-dom';
import { Form, Button, Container, Row, Col, Card, Alert } from 'react-bootstrap';

function RegistrationPage() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [message, setMessage] = useState('');
    const navigate = useNavigate();

    const handleRegister = async (e) => {
        e.preventDefault();
        try {
            const response = await api.post('/auth/register', { username, password });
            setMessage(response.data.message);
            navigate('/login');
        } catch (error) {
            if (error.response) {
                setMessage(error.response.data.message);
            } else {
                setMessage('An error occurred. Please try again later.');
            }
        }
    };

    return (
        <Container>
            <Row className="justify-content-md-center mt-5">
                <Col md={6} lg={4}>
                    <Card>
                        <Card.Body>
                            <h2 className="text-center mb-4">Register</h2>
                            {message && <Alert variant="info">{message}</Alert>}
                            <Form onSubmit={handleRegister}>
                                <Form.Group className="mb-3" controlId="formBasicUsername">
                                    <Form.Label>Username</Form.Label>
                                    <Form.Control
                                        type="text"
                                        placeholder="Enter username"
                                        value={username}
                                        onChange={(e) => setUsername(e.target.value)}
                                    />
                                </Form.Group>

                                <Form.Group className="mb-3" controlId="formBasicPassword">
                                    <Form.Label>Password</Form.Label>
                                    <Form.Control
                                        type="password"
                                        placeholder="Password"
                                        value={password}
                                        onChange={(e) => setPassword(e.target.value)}
                                    />
                                </Form.Group>

                                <Button variant="primary" type="submit" className="w-100">
                                    Register
                                </Button>
                            </Form>
                        </Card.Body>
                    </Card>
                </Col>
            </Row>
        </Container>
    );
}

export default RegistrationPage;

