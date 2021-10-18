/* REACT */
import React from 'react';
import { useParams, useRouteMatch } from "react-router-dom";
/* REDUX */
import {useAppDispatch, useAppSelector} from '../../../../app/hooks';
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
import StatBlock from "../../../../components/StatBlock";

const Details = ()=> {

  
  return (
    <Container>
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
            <Col>
              <div  >
                <Button> MINIMAP PLACEHOLDER</Button>
              </div>
            </Col>
        </Row>
    </Container>
  );
}

export default Details;