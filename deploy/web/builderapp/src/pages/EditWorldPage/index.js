/* REACT */
import React from 'react';
import { useParams, useRouteMatch, useHistory } from "react-router-dom";
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
import WorldEditRoutes from "./WorldEditRoutes"


const EditWorldPage = ()=> {
  const history = useHistory();
  let { worldId } = useParams();
  let { path, url } = useRouteMatch();

  function handleClick(sectionName) {
    history.push(`${url}/${sectionName}`);
  }
  
  return (
    <Container>
        <Row>
          <Col xs={2}>
                  <ButtonGroup vertical>
                    <Button 
                      variant="outline-secondary" 
                      onClick={()=>handleClick("details")}
                    >
                      Details
                    </Button>
                    <Button 
                      variant="outline-secondary" 
                      onClick={()=>handleClick("rooms")}
                    >
                      Rooms
                    </Button>
                    <Button 
                      variant="outline-secondary" 
                      onClick={()=>handleClick("characters")}
                    >
                      Characters
                    </Button>
                    <Button 
                      variant="outline-secondary" 
                      onClick={()=>handleClick("objects")}
                    >
                      Objects
                    </Button>
                    <Button 
                      variant="outline-secondary" 
                      onClick={()=>handleClick("interactions")}
                    >
                      Interactions
                    </Button>
                    <Button 
                      variant="outline-secondary" 
                      onClick={()=>handleClick("quests")}
                    >
                      Quests
                    </Button>
                  </ButtonGroup>
          </Col>
          <Col>
            <WorldEditRoutes/>
          </Col>
        </Row>
    </Container>
  );
}

export default EditWorldPage;