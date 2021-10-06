/* REACT */
import React from 'react';
import { useParams } from "react-router-dom";
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
import StatBlock from "../../components/StatBlock";

const EditWorldPage = ()=> {

  let { worldId } = useParams();
  
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
            <Col>
              <Row>
                <Col>
                  <Row>
                    <StatBlock
                      title={"Configuration"}
                      fieldNames={["Peaceful", "Heuristic Trading"]}
                      data={{}}
                    />
                  </Row>
                  <Row>
                    <StatBlock
                      title={"Statistics"}
                      fieldNames={["Room count", "Object Count", "Character count", "- Playable characters", "- NPC-only characters", "OtherStats"]}
                      data={{}}
                    />
                  </Row>
                </Col>
              </Row>
            </Col>
            <Col>
          </Col>  
          </Col>
        </Row>
    </Container>
  );
}

export default EditWorldPage;