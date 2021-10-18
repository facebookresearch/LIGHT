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
/* CUSTOM COMPONENTS */
import TextInput from "../../components/FormFields/TextInput"
import GenerateForms from "../../components/FormFields/GenerateForms"
import BreadCrumbs from "../../components/BreadCrumbs"
//DUMMY DATE
import DummyData from "../../Copy/DummyData"

const RoomPage = ()=> {
    const history = useHistory();
    let { worldId, categories, roomid } = useParams();
    let currentData=DummyData[worldId]
    let roomList = currentData.rooms
    let currentRoom = roomList[roomid]
    const handleClick = ()=>{

        history.push(`/editworld/${worldId}/${categories}/map/rooms/${roomid}/`);
      }
    //CRUMBS
    const crumbs= [{name:` Overview` , linkUrl:`/editworld/${worldId}/${categories}`}, {name:` Map` , linkUrl:`/editworld/${worldId}/${categories}/map`},  {name:` Room:  ${currentRoom.name}` , linkUrl:`/editworld/${worldId}/${categories}/map/rooms/${roomid}`}]
    return (
        <Container>
            <Row>
                <BreadCrumbs 
                    crumbs={crumbs}
                />
            </Row>
            <Row>
                <Col>
                    <Row>
                        <TextInput
                            label="Room Name"
                        />
                    </Row>
                    <Row>
                        <GenerateForms label="Room Description:" />
                    </Row>
                    <Row>
                        <GenerateForms label="Room Characters:" />
                    </Row>
                    <Row>
                        <GenerateForms label="Room Objects:" />
                    </Row>
                </Col>
                <Col>
                    <Row>
                        
                    </Row>
                    <Row>
                        
                    </Row>
                    <Row>
                        
                    </Row>
                </Col>
            </Row>
        </Container>
    );
}
export default RoomPage;