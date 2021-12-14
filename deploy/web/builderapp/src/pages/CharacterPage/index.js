/* REACT */
import React, {useState, useEffect} from 'react';
import { useParams, useRouteMatch, useHistory } from "react-router-dom";
/* REDUX */
import {useAppDispatch, useAppSelector} from '../../app/hooks';
/* ---- REDUCER ACTIONS ---- */
import { fetchWorlds, selectWorld } from "../../features/playerWorlds/playerworlds-slice.ts";
import { updateRooms, selectRoom} from "../../features/rooms/rooms-slice.ts";
import { updateCharacters, selectCharacter } from "../../features/characters/characters-slice.ts";
/* STYLES */
import './styles.css';
/* BOOTSTRAP COMPONENTS */
//LAYOUT
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
/* CUSTOM COMPONENTS */
import GenerateForms from "../../components/FormFields/GenerateForms"
import TextInput from "../../components/FormFields/TextInput"
import ButtonToggle from "../../components/FormFields/ButtonToggle"
import Slider from "../../components/FormFields/Slider"
import BreadCrumbs from "../../components/BreadCrumbs"

const CharacterPage = ()=> {
      //REACT ROUTER
      const history = useHistory();
      let { worldId, roomid, charid } = useParams();
      /* REDUX DISPATCH FUNCTION */
      const dispatch = useAppDispatch();
      /* ------ REDUX STATE ------ */
      //WORLDS
      const customWorlds = useAppSelector((state) => state.playerWorlds.customWorlds);
      const selectedWorld = useAppSelector((state) => state.playerWorlds.selectedWorld);
      const selectedRoom = useAppSelector((state) => state.worldRooms.selectedRoom)
      const selectedCharacter = useAppSelector((state) => state.worldCharacters.selectedCharacter)
      /* ------ LOCAL STATE ------ */
  
      //UTILS
  
      /* --- LIFE CYCLE FUNCTIONS --- */
      useEffect(()=>{
          if(customWorlds.length){
              customWorlds.map((world) =>{
                  const {id} = world;
                  if(worldId == id){
                      dispatch(selectWorld(world))
                  }
              })
          }
      },[customWorlds])
  
      useEffect(()=>{
          if(selectedWorld){
              let {nodes}= selectedWorld
              let currentRoom = nodes[roomid]
              console.log("CURRENT ROOMS", currentRoom)
              dispatch(selectRoom(currentRoom))
          }
        },[selectedWorld])
      
        useEffect(()=>{
          if(selectedWorld){
              let {nodes}= selectedWorld
              let currentCharacter = nodes[charid]
              console.log("CURRENT CHARACTERS", currentCharacter)
              dispatch(selectCharacter(currentCharacter))
          }
        },[selectedWorld])
  
  //CRUMBS
  const crumbs= [{name:` Overview` , linkUrl:`/editworld/${worldId}/details`}, {name:` Map` , linkUrl:`/editworld/${worldId}/details/map`},  {name:` Room:  ${selectedRoom.name}` , linkUrl:`/editworld/${worldId}/details/map/rooms/${roomid}`},{name:` Map` , linkUrl:`/editworld/${worldId}/details/map`},  {name:` Character:  ${selectedCharacter.name}` , linkUrl:`/editworld/${worldId}/details/map/rooms/${roomid}`} ]
  
  return (
    <Container>
            {
            selectedCharacter
            ?
            <>
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
                        <h5>{selectedRoom.description}</h5>
                    </Row>
                    <Row>
                        <h5>Attributes</h5>
                    </Row>
                    <Row>

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
            </>
            :
            <div/>
            }
    </Container>
  );
}

export default CharacterPage;