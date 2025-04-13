import React from "react";
import { Navbar, Nav, Container } from "react-bootstrap";
import { FaHotel, FaRobot, FaThList } from "react-icons/fa";
import "bootstrap/dist/css/bootstrap.min.css";

const CustomNavbar = () => {
  return (
    <Navbar bg="dark" variant="dark" expand="lg" sticky="top" className="shadow-sm">
      <Container>
        <Navbar.Brand href="#" className="d-flex align-items-center gap-2">
          <FaHotel className="text-info" /> HotelAI
        </Navbar.Brand>
        <Navbar.Toggle aria-controls="basic-navbar-nav" />
        <Navbar.Collapse id="basic-navbar-nav">
          <Nav className="ms-auto gap-3">
            <Nav.Link href="#chat">
              <FaRobot className="me-1" /> ChatBot
            </Nav.Link>
            <Nav.Link href="#dashboard">
              <FaThList className="me-1" /> Dashboard
            </Nav.Link>
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
};

export default CustomNavbar;
