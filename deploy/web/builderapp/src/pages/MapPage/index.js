/* REACT */
import React, {useEffect} from 'react';
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
import Button from 'react-bootstrap/Button'
/* CUSTOM COMPONENTS */
import BreadCrumbs from "../../components/BreadCrumbs"

const MapPage = ()=> {
//REACT ROUTER
  const history = useHistory();
  let { worldId, categories } = useParams(); 
  const handleClick = (sectionName)=>{
    history.push(`/editworld/${worldId}/${sectionName}`);
  }
//CRUMBS
  const crumbs= [{name:` Overview` , linkUrl:`/editworld/${worldId}/${categories}`}, {name:` Map` , linkUrl:`/editworld/${worldId}/${categories}/map`}]
  return (
    <Container>
        <Row>
            <BreadCrumbs 
                crumbs={crumbs}
            />
        </Row>
        <Row>
            
        </Row>
        <Row>
            <Col>
                <Button></Button>
            </Col>
            <Col>
                <Button></Button>
            </Col>
            <Col>
                <Button></Button>
            </Col>
        </Row>
    </Container>
  );
}

export default MapPage;