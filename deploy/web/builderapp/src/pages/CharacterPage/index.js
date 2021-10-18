/* REACT */
import React from 'react';
import { useParams, useRouteMatch } from "react-router-dom";
/* REDUX */
import {useAppDispatch, useAppSelector} from '../../app/hooks';
/* STYLES */
import './styles.css';
/* BOOTSTRAP COMPONENTS */
//LAYOUT
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
/* CUSTOM COMPONENTS */
import GenerateForms from "../../components/FormFields/GenerateForms"

const CharacterPage = ()=> {

  
  return (
    <Container>
        <Row>
            <Col>
              <Row>
                <GenerateForms label="Character Description:" />
              </Row>
              <Row>
                
              </Row>
            </Col>
            <Col>
              
              </Col>
        </Row>
    </Container>
  );
}

export default CharacterPage;