/* REACT */
import React from 'react';
import { useParams, useRouteMatch, useHistory } from "react-router-dom";
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
  //REACT ROUTER
  const history = useHistory();
  let { worldId, categories } = useParams();
  /* ------ REDUX STATE ------ */
  //WORLDS
  const selectedWorld = useAppSelector((state) => state.playerWorlds.selectedWorld);
  /* ------ HANDLERS ------ */
  const handleClick = ()=>{
    history.push(`/editworld/${worldId}/${"details"}/map`);
  }
  
  return (
    <Container>
        <Row>
            <Col>
              <Row>
                  <StatBlock
                    key="config"
                    title={"Configuration"}
                    fieldNames={["Peaceful", "Heuristic Trading"]}
                    data={{}}
                  />
              </Row>
              <Row>
                  <StatBlock
                    key="statistics"
                    title={"Statistics"}
                    fieldNames={["Room count", "Object Count", "Character count", "- Playable characters", "- NPC-only characters", "OtherStats"]}
                    data={{}}
                  />
              </Row>
            </Col>
            <Col>
              <div  >
                <Button onClick={handleClick}> MINIMAP PLACEHOLDER</Button>
              </div>
            </Col>
        </Row>
    </Container>
  );
}

export default Details;