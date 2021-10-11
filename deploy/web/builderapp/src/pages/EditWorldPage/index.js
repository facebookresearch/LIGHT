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
//BUTTON
import ButtonGroup from 'react-bootstrap/ButtonGroup'
import Button from 'react-bootstrap/Button'
/* CUSTOM COMPONENTS */


const EditWorldPage = ()=> {

  let { worldId } = useParams();
  let { path, url } = useRouteMatch();
  
  return (
    <Container>
        {worldId}
        <Row>
          <Col xs={2}>
                  <ButtonGroup vertical>
                    <Button variant="outline-secondary" >Details</Button>
                    <Button variant="outline-secondary">Rooms</Button>
                    <Button variant="outline-secondary">Characters</Button>
                    <Button variant="outline-secondary">Objects</Button>
                    <Button variant="outline-secondary">Interactions</Button>
                    <Button variant="outline-secondary">Quests</Button>
                  </ButtonGroup>
          </Col>
          <Col>
            {}
          </Col>
        </Row>
    </Container>
  );
}

export default EditWorldPage;