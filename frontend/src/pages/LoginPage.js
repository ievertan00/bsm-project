import React, { useState, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from '../AuthContext';
import { Form, Button, Container, Row, Col, Card, Alert } from 'react-bootstrap';
import api from '../api';

function LoginPage() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [message, setMessage] = useState('');
    const { login } = useContext(AuthContext);
    const navigate = useNavigate();

    const handleLogin = async (e) => {
        e.preventDefault();
        try {
            const response = await api.post('/auth/login', { username, password }, { withCredentials: true });
            setMessage(response.data.message);
            login(username);
            navigate('/dashboard');
        } catch (error) {
            console.error('Login error:', error);
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
                            <h2 className="text-center mb-4">Login</h2>
                            {message && <Alert variant="danger">{message}</Alert>}
                            <Form onSubmit={handleLogin}>
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
                                    Login
                                </Button>
                            </Form>
                        </Card.Body>
                    </Card>
                </Col>
            </Row>
        </Container>
    );
}

export default LoginPage;

