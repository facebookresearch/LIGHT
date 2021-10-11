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
/* CUSTOM COMPONENTS */
import StatBlock from "../../../../components/StatBlock";

const Characters = ()=> {

  
  return (
    <Container>
      CHARACTERS
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
    </Container>
  );
}

export default Characters;