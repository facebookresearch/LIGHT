/* REACT */
import React, {useState, useEffect} from 'react';
/* REDUX */
import {useAppDispatch, useAppSelector} from '../../../../app/hooks';
/* ---- REDUCER ACTIONS ---- */
import {  setTaskRouterCurrentLocation, updateTaskRouterHistory } from "../../../../features/taskRouter/taskrouter-slice.ts";
/* STYLES */
import "./styles.css";
/* BOOTSTRAP COMPONENTS */

/* CUSTOM COMPONENTS */
import TypeAheadTokenizerForm from "../../../../components/world_builder/FormFields/TypeAheadTokenizer"
/* BOOTSTRAP COMPONENTS */
import Button from 'react-bootstrap/Button'
/* STYLES */
import "./styles.css"



const BasicEditRoom = ({
    saveFunction,
    addContent,
    addRoom,
    updateRoom,
    deleteRoom,
    addCharacter,
    updateCharacter,
    deleteCharacter,
    addObject,
    updateObject,
    deleteObject,
    api,
    builderRouterNavigate,
})=> {

                /*** NOTES/TODOS ***/
    //1.  Connect recommendations to selectedWorld State. X
    //2.  Discuss Adding api reply that alerts user to not having any suggestions. X
    //3.  Add isLoading state and spinner with overlay for async API interactions.
    //4.  Track Changes and block save button usage if nothing new is being applied.
    //5.  Connect Local State more thought fully when it is updating selected room.
    //6.  All formatting and updating when using the Common Sense API can be applied to Advanced Pages.
    //7.  Rebuild lifecycle function here



    // Common sense API
    let {
        getRoomAttributes,
        getRoomFill,
        suggestRoomContents,
        suggestCharacterContents,
        suggestObjectContents,
        getObjectFill,
        getCharacterFill,
    } = api;

    /* REDUX DISPATCH FUNCTION */
    const dispatch = useAppDispatch();
    /* ------ REDUX STATE ------ */
    //TASKROUTER
    const currentLocation = useAppSelector((state) => state.taskRouter.currentLocation);
    const taskRouterHistory = useAppSelector((state) => state.taskRouter.taskRouterHistory);
    //WORLDS
    const worldDraft = useAppSelector((state) => state.playerWorld.worldDraft);
    const selectedWorld = useAppSelector((state) => state.playerWorld.selectedWorld);
    //ROOMS
    const worldRooms = useAppSelector((state) => state.worldRooms.worldRooms);
    const selectedRoom = useAppSelector((state) => state.worldRooms.selectedRoom);
    //CHARACTERS
    const worldCharacters = useAppSelector((state) => state.worldCharacters.worldCharacters);
    //OBJECTS
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
    //Sets isNewRoom state boolean based on presence of node_id.  This boolean determines rendered form fields and save on click function
    useEffect(()=>{
        if(selectedRoom.node_id){
            setIsNewRoom(false)
        }else{
            setIsNewRoom(true)
        }
        setCurrentRoomData(selectedRoom)
    },[selectedRoom])

    //Upon any changes to world rooms, current room data, or world draft, room will update fields
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
    }, [currentRoomData, worldRooms, selectedWorld])

    //HANDLERS
    //WORLD DRAFT
    //Saves any changes to world draft
    const SaveHandler = ()=>{
        saveFunction()
    }

    //NAVIGATION
    //Navigates to room's advanced edit page
    const handleAdvancedClick = ()=>{
        saveFunction()
        let updatedLocation = {
            name:"rooms",
            id: formattedRoomId
        };
        console.log("CURRENT LOCATION:  ", updatedLocation)
        window.localStorage.setItem("currentLocation", JSON.stringify(updatedLocation))
        builderRouterNavigate(updatedLocation)
    }

    //the function that clicking a gear on the typeahead tokenizer invokes.  It saves the current worldState to the draft before navigating to the item or character's advanced page.
    const handleBasicGearClick = (newLoc)=>{
        saveFunction()
        const {node_id} = selectedRoom;
        console.log("BASIC GEAR CLICK:  ", node_id)
        let roomLocation = {
            name:"rooms",
            id: node_id
        };
        let updatedGearLocation = newLoc;
        const updatedRouterHistory = [...taskRouterHistory, currentLocation, roomLocation]
        console.log("BASIC UPDATED HISTORY:  ", updatedRouterHistory);
        dispatch(updateTaskRouterHistory(updatedRouterHistory));
        console.log("CURRENT LOCATION:  ", updatedGearLocation);
        dispatch(setTaskRouterCurrentLocation(updatedGearLocation));
    }

    // * NOTE:  Condense handlers next update
    // ROOM HANDLERS
    //Creates room assigning it only a name.  Add room generates node_id
    const RoomCreateHandler = () =>{
        let updatedSelectedRoom = {...selectedRoom, name: roomName }
        console.log("CREATE ROOM", updatedSelectedRoom)
        addRoom(updatedSelectedRoom)
    }

    //Deletes room from draft using selected room node_id
    const RoomDeleteHandler = ()=>{
        deleteRoom(selectedRoom.node_id)
    }
    //Changes Name of selected room.  Name is required for new room to be created
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

    //CHARACTER HANDLERS
    //Adds Character to room, changes will only change world draft upon clicking save button
    const AddCharacterHandler = (character)=>{
        console.log("ADDING CHARACTER DATA:  ", character)
        addCharacter(character)
        let updatedRoomCharacters = [...roomCharacters, character];
        setRoomCharacters(updatedRoomCharacters);
    }


    //Removes Character from room, changes will only change world draft upon clicking save button
    const RemoveCharacterHandler = (id)=>{
        console.log(" REMOVED CHARACTER ID:  ", id)
        deleteCharacter(id)
        let updatedRoomCharacters = roomCharacters.filter(obj=>obj.node_id!=id);
        setRoomCharacters(updatedRoomCharacters);
    }

    //OBJECT HANDLERS
    //Adds Object to room, changes will only change world draft upon clicking save button
    const AddObjectHandler = (obj)=>{
        console.log("ADDING OBJECT DATA:  ", obj)
        addObject(obj)
        let updatedRoomObjects = [...roomObjects, obj]
        setRoomObjects(updatedRoomObjects)
    }

    //Removes Object from room, changes will only change world draft upon clicking save button
    const RemoveObjectHandler = (id)=>{
        console.log(" REMOVED OBJECT ID:  ", id)
        deleteObject(id)
        let updatedRoomObjects = roomObjects.filter(obj=>obj.node_id!=id);
        setRoomObjects(updatedRoomObjects)
    }


    /* COMMON SENSE API INTERACTIONS */

    // COMMON SENSE DESCRIBE ROOM FUNCTION
    const CommonSenseDescribeRoom = ()=>{
        let target_room = selectedRoom['node_id'];
        let nodes = {};
        nodes[target_room] = selectedRoom;
        for (let character of worldCharacters) {
            nodes[character['node_id']] = character;
        }
        for (let object of worldObjects) {
            nodes[object['node_id']] = object;
        }
        let agents = worldCharacters.map(c => c['node_id']);
        let objects = worldObjects.map(c => c['node_id']);
        let rooms = [target_room]
        let room_graph = {nodes, agents, objects, rooms};
        console.log("room graph");
        console.log(room_graph);
        console.log("selectedRoom");
        console.log(target_room);
        getRoomAttributes({target_room, room_graph}).then((result) => {
            console.log("Finished describe room");

            console.log(result);
        })
    }
    // COMMON SENSE FORM FUNCTION
    const CommonSenseRoomContents = ()=>{
        let target_room = selectedRoom['node_id'];
        let nodes = {};
        nodes[target_room] = selectedRoom;
        for (let character of worldCharacters) {
            nodes[character['node_id']] = character;
        }
        for (let object of worldObjects) {
            nodes[object['node_id']] = object;
        }
        let agents = worldCharacters.map(c => c['node_id']);
        let objects = worldObjects.map(c => c['node_id']);
        let rooms = [target_room]
        let room_graph = {nodes, agents, objects, rooms};
        console.log("room graph");
        console.log(room_graph);
        console.log("selectedRoom");
        console.log(target_room);
        suggestRoomContents({target_room, room_graph}).then((result) => {
            console.log("Finished Describe");
            console.log(result);
            const newItems = result.new_items;
            addContent(target_room, newItems)
        })
    }

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
                <Button onClick={CommonSenseDescribeRoom}>
                    DESCRIBE ROOM
                </Button>
                <Button onClick={CommonSenseRoomContents}>
                    SUGGEST ROOM CONTENTS
                </Button>
                {/* <Button onClick={CommonSenseClickHandler}>
                    FILL IN OBJECTS
                </Button>
                <Button onClick={CommonSenseClickHandler}>
                    FILL IN CHARACTERS
                </Button> */}
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
                            sectionName={"characters"}
                            roomId={formattedRoomId}
                            tokenType={"characters"}
                            tokens={roomCharacters}
                            onTokenAddition={AddCharacterHandler}
                            onTokenRemoval={RemoveCharacterHandler}
                            builderRouterNavigate={handleBasicGearClick}
                        />
                        <TypeAheadTokenizerForm
                            formLabel="OBJECTS"
                            tokenOptions={worldObjects}
                            sectionName={"objects"}
                            roomId={formattedRoomId}
                            tokenType={"objects"}
                            tokens={roomObjects}
                            onTokenAddition={AddObjectHandler}
                            onTokenRemoval={RemoveObjectHandler}
                            builderRouterNavigate={handleBasicGearClick}
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
