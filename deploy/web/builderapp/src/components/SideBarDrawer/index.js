/* REACT */
import React from 'react';
import { useParams, useRouteMatch } from "react-router-dom";
/* REDUX */

/* STYLES */
import './styles.css';
/* BOOTSTRAP COMPONENTS */
//LAYOUT
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Offcanvas from 'react-bootstrap/Offcanvas'
/* CUSTOM COMPONENTS */


const SideBarDrawer = ({
    showSideBar,
    closeSideBarFunction, 
    children
})=> {

  
  return (
    <Offcanvas 
        show={showSideBar} 
        onHide={closeSideBarFunction}
        backdrop={false}
    >
        <Offcanvas.Header closeButton>
            <Offcanvas.Title>Offcanvas</Offcanvas.Title>
        </Offcanvas.Header>
        <Offcanvas.Body>
           {children}
        </Offcanvas.Body>
    </Offcanvas>
  );
}

export default SideBarDrawer;