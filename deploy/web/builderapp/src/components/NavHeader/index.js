
/*****
 * Copyright (c) Meta Platforms, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React from "react";
/* REACT ROUTER */
import { Link } from 'react-router-dom';
/* STYLES */
import "./styles.css";
/* BOOTSTRAP COMPONENTS */
// LAYOUT
import Container from 'react-bootstrap/Container'
import Row from 'react-bootstrap/Row'
import Col from 'react-bootstrap/Col'
//COMPONENTS
import Navbar from 'react-bootstrap/Navbar';
import Nav from 'react-bootstrap/Nav'
import Button from 'react-bootstrap/Button'
/* IMAGES */
import Scribe from "../../assets/images/scribe.png"

//Navheader - 
const Navheader = ({ }) => {
  return (
  <Navbar id="navbar" bg="dark" variant="dark" sticky="top" >
          <Navbar.Brand href="#home">
            <img
              alt=""
              src={Scribe}
              width="30"
              height="30"
              className="d-inline-block align-top"
            />{' '}
          <span className="light-logo">
            LIGHT
          </span>
          {' '}
            WORLD BUILDER
          {' '}
          </Navbar.Brand>
          <Nav className="mr-auto">
                  <Nav.Item eventkey={1} href="/">
                    <Nav.Link as={Link} to="/" >HELP</Nav.Link>
                  </Nav.Item>
          </Nav>
          <Nav className="mr-auto">
                  <Nav.Item eventkey={1} href="/">
                    <Nav.Link as={Link} to="/" >BUILD HOME</Nav.Link>
                  </Nav.Item>
          </Nav>
          <Nav className="mr-auto">
                  <Nav.Item eventkey={1} href="/">
                    <Nav.Link as={Link} to="/" >MAIN HOME</Nav.Link>
                  </Nav.Item>
          </Nav>
  </Navbar>
  );
};

export default Navheader;