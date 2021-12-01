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
    const selectedRoom = useAppSelector((state) => state.worldRooms.selectedRoom)
    /* ------ LOCAL STATE ------ */

    //UTILS


    /* --- LIFE CYCLE FUNCTIONS --- */

    //HANDLERS
    const handleClick = (roomId)=>{
        history.push(`/editworld/${worldId}/${categories}/map/rooms/${roomId}`);
    }

    return (
        <div className="basiceditroom-container">
            <div>
                <Button>
                    Describe it!
                </Button>
                <Button>
                    Advanced
                </Button>
            </div>
            <div>
                <TypeAheadTokenizerForm
                    formLabel="Room Name:"
                />
                <TypeAheadTokenizerForm
                    formLabel="Description:"
                />
                <TypeAheadTokenizerForm
                    formLabel="Characters:"
                />
                <TypeAheadTokenizerForm
                    formLabel="Objects:"
                />
                <input/>
            </div>
        </div>
    );
    }

export default BasicEditRoom;