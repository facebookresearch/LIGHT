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
import WorldEditBody from "./WorldEditBody"
import ButtonGroups from "../../components/ButtonGroups"


const EditWorldPage = ()=> {
  const history = useHistory();
  let { worldId, categories } = useParams();
  let { path, url } = useRouteMatch();

  const handleClick = (sectionName)=>{
    history.push(`/editworld/${worldId}/${sectionName}`);
  }
  const SideBarButtons = [
    {
      name: "details",
      clickFunction: () => handleClick("details"),
      activeCondition: (categories == "details")
    },
    {
      name: "characters",
      clickFunction: () => handleClick("characters"),
      activeCondition: (categories == "characters")
    },
    {
      name: "rooms",
      clickFunction: () => handleClick("rooms"),
      activeCondition: (categories == "rooms")
    },
    {
      name: "quests",
      clickFunction: () => handleClick("quests"),
      activeCondition: (categories == "quests")
    },
    {
      name: "objects",
      clickFunction: () => handleClick("objects"),
      activeCondition: (categories == "objects")
    },
    {
      name: "interactions",
      clickFunction: () => handleClick("interactions"),
      activeCondition: (categories == "interactions")
    }
  ];
  
  return (
    <Container>
        <Row>
          <Col xs={2}>
            <ButtonGroups 
              buttons={SideBarButtons}
            />
          </Col>
          <Col>
            <WorldEditBody/>
          </Col>
        </Row>
    </Container>
  );
}

export default EditWorldPage;