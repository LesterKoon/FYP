import React, { useState } from 'react';
import { Navbar, Nav, NavDropdown, Container } from 'react-bootstrap';
import { NavLink, useLocation } from 'react-router-dom';
import './components.css';
import 'bootstrap/dist/css/bootstrap.min.css';


const AppNavbar = () => {
    const [showDropdown, setShowDropdown] = useState(false);
    const [expanded, setExpanded] = useState(false);

    const handleMouseEnter = () => setShowDropdown(true);
    const handleMouseLeave = () => setShowDropdown(false);

    const location = useLocation();

    const isRecommendationsActive =
        location.pathname === '/chatbot' ||
        location.pathname === '/add-playlist';

    const handleNavLinkClick = () => setExpanded(false);

    return (
        <Navbar className="navbar d-flex align-items-center" expand="lg" expanded={expanded}>
            <Container className="container">
                <Navbar.Brand className="nav-brand d-flex align-items-center">
                    <img
                    src="/assets/icon_light.png"
                    alt="VibeSync logo"
                    />
                    <img
                    src="/assets/txt_logo_light.png"
                    alt="VibeSync logo"
                    className="d-none d-sm-block"
                    />
                </Navbar.Brand>
                <Navbar.Toggle aria-controls="basic-navbar-nav" onClick={() => setExpanded(!expanded)}/>
                <Navbar.Collapse id="basic-navbar-nav">
                    <Nav className="me-auto">
                        <Nav.Link as={NavLink} to="/" className="nav-link" onClick={handleNavLinkClick}>
                            Home
                        </Nav.Link>
                        <NavDropdown title={<span className={isRecommendationsActive ? 'drop-active' : ''}>Recommendations</span>}
                            id="basic-nav-dropdown"                             
                            show={showDropdown}
                            onMouseEnter={handleMouseEnter}
                            onMouseLeave={handleMouseLeave}
                            >
                            <NavDropdown.Item as={NavLink} to="/chatbot" onClick={handleNavLinkClick}>
                                Chatbot
                            </NavDropdown.Item>
                            <NavDropdown.Item as={NavLink} to="/add-playlist" onClick={handleNavLinkClick}>
                                Add Playlist
                            </NavDropdown.Item>
                        </NavDropdown>
                        <Nav.Link as={NavLink} to="/explore" className="nav-link" onClick={handleNavLinkClick}>
                            Explore
                        </Nav.Link>
                    </Nav>
                </Navbar.Collapse>
            </Container>
        </Navbar>
    );
};

export default AppNavbar;