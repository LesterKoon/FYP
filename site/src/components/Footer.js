import React from "react";
import { Container, Row, Col, Button } from "react-bootstrap";
import "./components.css"; // Create this file for footer-specific styles

const Footer = () => {
    return (
        <footer className="footer">
            <Container fluid>
                <Row className="align-items-center">
                    <Col xs={12} md={6} className="footer-left text-md-start text-md-start text-center">
                    <a href="https://github.com/LesterKoon" target="_blank" rel="noopener noreferrer">
                    <img
                        src="/assets/github.svg"
                        alt="GitHub"
                        title="GitHub"
                        className="icon"
                    />
                    </a>
                    <a href="https://www.linkedin.com/in/lesterkoon/" target="_blank" rel="noopener noreferrer">
                    <img
                        src="/assets/linkedin.svg"
                        alt="LinkedIn"
                        title="LinkedIn"
                        className="icon"
                    />
                    </a>
                    <a href="mailto:lester.koon.zm@gmail.com" target="_blank" rel="noopener noreferrer">
                    <img
                        src="/assets/mail.svg"
                        alt="E-mail"
                        title="Email"
                        className="icon"
                    />
                    </a>
                    <a href="http://localhost:3000/" target="_blank" rel="noopener noreferrer">
                    <img
                        src="/assets/rpaper.svg"
                        alt="Research Paper"
                        title="Research Paper"
                        className="icon"
                    />
                    </a>
                    </Col>
                    <Col xs={12} md={6} className="footer-right text-md-end text-center">
                        <p className="footer-text">
                        &copy; {new Date().getFullYear()} VibeSync. All rights reserved.
                        </p>
                        <Button variant="primary" href="https://forms.gle/kkcfGJWXNQ5seFxT6" target="_blank" rel="noopener noreferrer" class="feedback-button">
                            Send Feedback
                        </Button>
                    </Col>
                </Row>
                <Row>
                    <Col className="text-center">
                        <p className="footer-text">
                            Lester Koon - Sunway University
                        </p>
                    </Col>
                </Row>
            </Container>
        </footer>
    );
};

export default Footer;
