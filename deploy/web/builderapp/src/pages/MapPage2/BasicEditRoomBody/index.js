/* REACT */
import React, {useState, useEffect} from 'react';
import { useParams, useRouteMatch, useHistory } from "react-router-dom";
/* REDUX */
import {useAppDispatch, useAppSelector} from '../../../app/hooks';
/* ---- REDUCER ACTIONS ---- */
import { updateRooms, selectRoom, updateSelectedRoom} from "../../../features/rooms/rooms-slice.ts";
import { updateObjects} from "../../../features/objects/objects-slice.ts";
import { updateCharacters } from "../../../features/characters/characters-slice.ts";
/* STYLES */
import "./styles.css";
/* BOOTSTRAP COMPONENTS */
//LAYOUT
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
/* CUSTOM COMPONENTS */
import TypeAheadTokenizerForm from "../../../components/FormFields/TypeAheadTokenizer"
/* BLUEPRINT JS COMPONENTS */
import {
  NumericInput,
  InputGroup,
  ControlGroup,
  FormGroup,
  Tooltip,
  Position,
  Icon,
  Switch,
  Button,
} from "@blueprintjs/core";
/* STYLES */
import "./styles.css"

const BasicEditRoom = ()=> { 
    //REACT ROUTER
    const history = useHistory();
    let { worldId, categories } = useParams();
    //let { path, url } = useRouteMatch();
    /* REDUX DISPATCH FUNCTION */
    const dispatch = useAppDispatch();
    /* ------ REDUX STATE ------ */
    const worldRooms = useAppSelector((state) => state.worldRooms.worldRooms);
    const selectedRoom = useAppSelector((state) => state.worldRooms.selectedRoom);
    const worldCharacters = useAppSelector((state) => state.worldCharacters.worldCharacters);
    const worldObjects = useAppSelector((state) => state.worldObjects.worldObjects);
    /* ------ LOCAL STATE ------ */

    //UTILS


    /* --- LIFE CYCLE FUNCTIONS --- */

    //HANDLERS
    const handleAdvancedClick = ()=>{
        const {node_id} = selectedRoom
        let formattedRoomId = node_id.replace(" ", "_");
        history.push(`/editworld/${worldId}/details/map/rooms/${formattedRoomId}`);
    }

    return (
        <div className="basiceditroom-container">
            <div>
                <Button onClick={handleAdvancedClick}>
                    Advanced
                </Button>
            </div>
            <div>
                <TypeAheadTokenizerForm
                    formLabel="Room Name:"
                    tokenOptions={worldRooms}
                />
                <input/>
                <TypeAheadTokenizerForm
                    formLabel="Characters:"
                    tokenOptions={worldCharacters}
                />
                <TypeAheadTokenizerForm
                    formLabel="Objects:"
                    tokenOptions={worldObjects}
                />
                <input/>
            </div>
        </div>
    );
    }

export default BasicEditRoom;