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
  Button,
} from "@blueprintjs/core";
/* STYLES */
import "./styles.css"

const BasicEditRoom = ({
    saveFunction,
    addRoom,
    updateRoom,
    deleteRoom,
    addCharacter,
    updateCharacter,
    deleteCharacter,
    addObject,
    updateObject,
    deleteObject,
})=> { 
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
    /* ------ REDUX ACTIONS ------ */


    /* ------ LOCAL STATE ------ */
    const [formattedRoomId, setFormattedRoomId] = useState(null)
    const [roomName, setRoomName] = useState("");
    const [roomCharacters, setRoomCharacters] =useState([]);
    const [roomObjects, setRoomObjects] =useState([]);

    /* --- LIFE CYCLE FUNCTIONS --- */
    useEffect(() => {
        const {node_id} = selectedRoom
        let updatedFormattedRoomId = node_id.replace(" ", "_");
        updatedFormattedRoomId = node_id.replace(" ", "_");
        console.log("updated roomId", updatedFormattedRoomId)
        setFormattedRoomId(updatedFormattedRoomId)
        let updatedRoomCharacters = worldCharacters.filter(char=>{
            let {container_node} = char;
            let {target_id} = container_node;
            return target_id == node_id
        })
        let updatedRoomObjects = worldObjects.filter(objs=>{
            let {container_node} = objs;
            let {target_id} = container_node;
            return target_id == node_id
        })
        console.log("NAME O", selectedRoom)
        setRoomName(selectedRoom.name)
        setRoomCharacters(updatedRoomCharacters)
        setRoomObjects(updatedRoomObjects)
    }, [selectedRoom])

    //HANDLERS
    const SaveHandler = ()=>{
        saveFunction()
    }

    const handleAdvancedClick = ()=>{
        history.push(`/editworld/${worldId}/details/map/rooms/${formattedRoomId}`);
    }

    // * NOTE:  Condense handlers next update
    const RoomNameChangeHandler = (e)=>{
        let updatedRoomName = e.target.value;
        let updatedSelectedRoom = {...selectedRoom, name: updatedRoomName }
        updateRoom(selectedRoom.id, updatedSelectedRoom)
        setRoomName(updatedRoomName)
    }

    const AddCharacterHandler = (character)=>{
        addCharacter(character)
        let updatedRoomCharacters = [...roomCharacters, character];
        setRoomCharacters(updatedRoomCharacters);
    }
    const AddObjectHandler = (obj)=>{
        let updatedRoomObjects = [...roomObjects, obj]
        setRoomObjects(updatedRoomObjects)
    }

    const RemovedCharacterHandler = (id)=>{
        let updatedRoomCharacters = roomCharacters.filter(obj=>obj.node_id==id);
        setRoomCharacters(updatedRoomCharacters);
    }

    const RemovedObjectHandler = (id)=>{
        let updatedRoomObjects = roomObjects.filter(obj=>obj.node_id==id);
        setRoomObjects(updatedRoomObjects)
    }

    //COMMON SENSE FORM FUNCTION
    const CommonSenseClickHandler = ()=>{}

    return (
        <div className="basiceditroom-container">
            <div className="basiceditroom-subheader">
                <Button onClick={handleAdvancedClick}>
                    ADVANCED EDITOR
                </Button>
                <Button onClick={CommonSenseClickHandler}>
                    DESCRIBE IT
                </Button>
            </div>
            <div className="basiceditroom-forms">
                <h5>
                    ROOM NAME
                </h5>
                <input className="basiceditroom-form" onChange={RoomNameChangeHandler} value={roomName}/>
                <TypeAheadTokenizerForm
                    formLabel="CHARACTERS"
                    tokenOptions={worldCharacters}
                    worldId={worldId}
                    sectionName={"characters"}
                    roomId={formattedRoomId}
                    defaultTokens={roomCharacters}
                    onTokenAddition={AddCharacterHandler}
                    onTokenRemoval={RemovedCharacterHandler}
                />
                <TypeAheadTokenizerForm
                    formLabel="OBJECTS"
                    tokenOptions={worldObjects}
                    worldId={worldId}
                    sectionName={"objects"}
                    roomId={formattedRoomId}
                    defaultTokens={roomObjects}
                    onTokenAddition={AddObjectHandler}
                    onTokenRemoval={RemovedObjectHandler}
                />
            </div>
            <div className="basiceditroom-button">
                <Button onClick={SaveHandler}>
                    SAVE
                </Button>
            </div>
        </div>
    );
    }

export default BasicEditRoom;