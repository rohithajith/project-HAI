import React from "react";
import { Navbar, Nav, Container, Button } from "react-bootstrap";
import { FaHotel, FaRobot, FaThList, FaSignOutAlt } from "react-icons/fa";
import "bootstrap/dist/css/bootstrap.min.css";

const CustomNavbar = ({ onLogout }) => {
  return (
    <Navbar bg="dark" variant="dark" expand="lg" sticky="top" className="shadow-sm">
      <Container>
        <Navbar.Brand href="#" className="d-flex align-items-center gap-2">
          <FaHotel className="text-info" /> HotelAI
        </Navbar.Brand>
        <Navbar.Toggle aria-controls="basic-navbar-nav" />
        <Navbar.Collapse id="basic-navbar-nav">
          <Nav className="me-auto gap-3">
            <Nav.Link href="#chat">
              <FaRobot className="me-1" /> ChatBot
            </Nav.Link>
            <Nav.Link href="#dashboard">
              <FaThList className="me-1" /> Dashboard
            </Nav.Link>
          </Nav>
          <Button variant="outline-light" onClick={onLogout} className="d-flex align-items-center">
            <FaSignOutAlt className="me-2" /> Logout
          </Button>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
};

export default CustomNavbar;
