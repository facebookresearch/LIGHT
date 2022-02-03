/* REACT */
import React, {useState, useEffect} from 'react';
import { useParams, useRouteMatch, useHistory } from "react-router-dom";
/* REDUX */
import {useAppDispatch, useAppSelector} from '../../../app/hooks';
/* ---- REDUCER ACTIONS ---- */

/* STYLES */
import "./styles.css";
/* BOOTSTRAP COMPONENTS */

/* CUSTOM COMPONENTS */
import TypeAheadTokenizerForm from "../../../components/FormFields/TypeAheadTokenizer"
/* BOOTSTRAP COMPONENTS */
import Button from 'react-bootstrap/Button'
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
    //WORLDS
    const worldDrafts = useAppSelector((state) => state.playerWorlds.worldDrafts);
    const worldRooms = useAppSelector((state) => state.worldRooms.worldRooms);
    const selectedRoom = useAppSelector((state) => state.worldRooms.selectedRoom);
    const worldCharacters = useAppSelector((state) => state.worldCharacters.worldCharacters);
    const worldObjects = useAppSelector((state) => state.worldObjects.worldObjects);
    /* ------ REDUX ACTIONS ------ */


    /* ------ LOCAL STATE ------ */
    const [currentRoomData, setCurrentRoomData] = useState(null)
    const [isNewRoom, setIsNewRoom] = useState(true)
    const [formattedRoomId, setFormattedRoomId] = useState(null)
    const [roomName, setRoomName] = useState("");
    const [roomCharacters, setRoomCharacters] =useState([]);
    const [roomObjects, setRoomObjects] =useState([]);

    /* --- LIFE CYCLE FUNCTIONS --- */
    useEffect(()=>{
        if(selectedRoom.node_id){
            setIsNewRoom(false)
        }else{
            setIsNewRoom(true)
        }
        setCurrentRoomData(selectedRoom)
    },[selectedRoom])

    useEffect(() => {
        if(selectedRoom){
            const {node_id} = selectedRoom;
            let updatedFormattedRoomId = node_id.replace(" ", "_");
            updatedFormattedRoomId = node_id.replace(" ", "_");
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
            setRoomName(selectedRoom.name)
            setRoomCharacters(updatedRoomCharacters)
            setRoomObjects(updatedRoomObjects)
        }
    }, [currentRoomData])

    //HANDLERS
    const SaveHandler = ()=>{
        saveFunction()
    }

    const RoomCreateHandler = () =>{
        let updatedSelectedRoom = {...selectedRoom, name: roomName }
        console.log("CREATE ROOM", updatedSelectedRoom)
        addRoom(updatedSelectedRoom)
    }

    const RoomDeleteHandler = ()=>{
        deleteRoom(selectedRoom.node_id)
    }

    const handleAdvancedClick = ()=>{
        history.push(`/editworld/${worldId}/details/map/rooms/${formattedRoomId}`);
    }

    // * NOTE:  Condense handlers next update
    const RoomNameChangeHandler = (e)=>{
        let updatedRoomName = e.target.value;
        let updatedSelectedRoom = {...selectedRoom, name: updatedRoomName }
        setRoomName(updatedRoomName)
        if(selectedRoom){
            if(selectedRoom.node_id){
                updateRoom(selectedRoom.node_id, updatedSelectedRoom)
            }
        }
    }

    const AddCharacterHandler = (character)=>{
        console.log("ADDING CHARACTER DATA:  ", character)
        addCharacter(character)
        let updatedRoomCharacters = [...roomCharacters, character];
        setRoomCharacters(updatedRoomCharacters);
    }
    const AddObjectHandler = (obj)=>{
        console.log("ADDING OBJECT DATA:  ", obj)
        addObject(obj)
        let updatedRoomObjects = [...roomObjects, obj]
        setRoomObjects(updatedRoomObjects)
    }

    const RemoveCharacterHandler = (id)=>{
        console.log(" REMOVED CHARACTER ID:  ", id)
        deleteCharacter(id)
        let updatedRoomCharacters = roomCharacters.filter(obj=>obj.node_id!=id);
        setRoomCharacters(updatedRoomCharacters);
    }

    const RemoveObjectHandler = (id)=>{
        console.log(" REMOVED OBJECT ID:  ", id)
        deleteObject(id)
        let updatedRoomObjects = roomObjects.filter(obj=>obj.node_id!=id);
        setRoomObjects(updatedRoomObjects)
    }

    //COMMON SENSE FORM FUNCTION
    const CommonSenseClickHandler = ()=>{}

    return (
        <div className="basiceditroom-container">
            <div className="basiceditroom-subheader">
                {
                    formattedRoomId ?
                    <Button onClick={handleAdvancedClick}>
                        ADVANCED EDITOR
                    </Button>
                    :
                    null
                }
                <Button onClick={CommonSenseClickHandler}>
                    DESCRIBE IT
                </Button>
            </div>
            <div className="basiceditroom-forms">
                <h5>
                    ROOM NAME
                </h5>
                <input className="basiceditroom-form" onChange={RoomNameChangeHandler} value={roomName}/>
                {
                    !isNewRoom ?
                    <>
                        <TypeAheadTokenizerForm
                            formLabel="CHARACTERS"
                            tokenOptions={worldCharacters}
                            worldId={worldId}
                            sectionName={"characters"}
                            roomId={formattedRoomId}
                            tokenType={"characters"}
                            tokens={roomCharacters}
                            onTokenAddition={AddCharacterHandler}
                            onTokenRemoval={RemoveCharacterHandler}
                        />
                        <TypeAheadTokenizerForm
                            formLabel="OBJECTS"
                            tokenOptions={worldObjects}
                            worldId={worldId}
                            sectionName={"objects"}
                            roomId={formattedRoomId}
                            tokenType={"objects"}
                            tokens={roomObjects}
                            onTokenAddition={AddObjectHandler}
                            onTokenRemoval={RemoveObjectHandler}
                        />
                    </>
                    :null
                }
            </div>
            <div className="basiceditroom-button">
                {
                    !isNewRoom ?
                    <Button onClick={SaveHandler}>
                        SAVE
                    </Button>
                    :
                    <Button 
                        onClick={RoomCreateHandler}
                        // disable={!roomName}
                    >
                        CREATE
                    </Button>
                }
                                {
                    !isNewRoom ?
                    <Button onClick={RoomDeleteHandler}>
                        DELETE
                    </Button>
                    :
                    null
                }
            </div>
        </div>
    );
    }

export default BasicEditRoom;