/* REACT */
import React, {useState, useEffect} from 'react';
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
import ButtonToggle from "../../components/FormFields/ButtonToggle"
import Slider from "../../components/FormFields/Slider"
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

    const buttonOptions = [
        {
            name: "Indoors",
            value:1
        },
        {
            name: "Outdoors",
            value:2
        },
    ]

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
                        <h5>In-Game appearance:</h5>
                    </Row>
                    <Row>
                        <h5>{currentRoom.description}</h5>
                    </Row>
                    <Row>
                        <h5>Attributes</h5>
                    </Row>
                    <Row>
                        <ButtonToggle
                            buttonOptions={buttonOptions}
                        />
                    </Row>
                    <Row>
                        <Slider 
                            label="Brightness"
                            maxLabel="The Sun"
                            minLabel="Pitch Black"
                        />
                    </Row>
                    <Row>
                        <Slider 
                            label="Temperature"
                            maxLabel="Hot"
                            minLabel="Cold"
                        />
                    </Row>
                </Col>
            </Row>
        </Container>
    );
}
export default RoomPage;