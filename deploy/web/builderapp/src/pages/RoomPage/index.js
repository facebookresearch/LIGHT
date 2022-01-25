/* REACT */
import React, {useState, useEffect} from 'react';
import { useParams, useRouteMatch, useHistory } from "react-router-dom";
/* REDUX */
import {useAppDispatch, useAppSelector} from '../../app/hooks';
/* ---- REDUCER ACTIONS ---- */
import { fetchWorlds, updateSelectedWorld, selectWorld, setWorldDrafts } from "../../features/playerWorlds/playerworlds-slice.ts";
import { updateRooms, selectRoom} from "../../features/rooms/rooms-slice.ts";
import { updateObjects} from "../../features/objects/objects-slice.ts";
import { updateCharacters } from "../../features/characters/characters-slice.ts";
/* STYLES */
import './styles.css';
/* BOOTSTRAP COMPONENTS */
//LAYOUT
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
/* CUSTOM COMPONENTS */
import TextInput from "../../components/FormFields/TextInput";
import ButtonToggle from "../../components/FormFields/ButtonToggle";
import Slider from "../../components/FormFields/Slider";
import GenerateForms from "../../components/FormFields/GenerateForms";
import BreadCrumbs from "../../components/BreadCrumbs";
import TypeAheadTokenizerForm from "../../components/FormFields/TypeAheadTokenizer";

const RoomPage = ()=> {
    //REACT ROUTER
    const history = useHistory();
    let { worldId, categories, roomid } = useParams();
    /* REDUX DISPATCH FUNCTION */
    const dispatch = useAppDispatch();
    /* ------ REDUX STATE ------ */
    //WORLD
    const worldDrafts = useAppSelector((state) => state.playerWorlds.worldDrafts);
    const selectedWorld = useAppSelector((state) => state.playerWorlds.selectedWorld);
    //ROOMS
    const worldRooms = useAppSelector((state) => state.worldRooms.worldRooms);
    const selectedRoom = useAppSelector((state) => state.worldRooms.selectedRoom);
    //OBJECTS
    const worldObjects = useAppSelector((state) => state.worldObjects.worldObjects);
    //CHARACTERS
    const worldCharacters = useAppSelector((state) => state.worldCharacters.worldCharacters);
    /* ------ REDUX ACTIONS ------ */
    //WORLD DRAFT
    const updateWorldsDraft = ()=>{
        let updatedWorlds = worldDrafts.map(world=> {
            if(world.id==worldId){
                return selectedWorld;
            }
            return world;
        })
        dispatch(setWorldDrafts(updatedWorlds))
    }
    //ROOMS
    const addRoom = (room)=>{
        let unupdatedWorld = selectedWorld;
        let {rooms, nodes } = unupdatedWorld;
        let formattedRoomId = room.id;
        while(rooms.indexOf(formattedRoomId)>=0){
            let splitFormattedRoomId = formattedRoomId.split("_")
            let idNumber = splitFormattedRoomId[splitFormattedRoomId.length-1]
            idNumber = idNumber++;
            splitFormattedRoomId[splitFormattedRoomId.length-1] = idNumber
            formattedRoomId = splitFormattedRoomId.join("_")
        }
        let updatedRoomData = {...room, node_id:formattedRoomId};
        let updatedRooms = [...rooms, formattedRoomId]
        let updatedNodes = {...nodes, [formattedRoomId]:updatedRoomData}
        let updatedWorld ={...selectedWorld, rooms: updatedRooms, nodes:updatedNodes}
        dispatch(updateSelectedWorld(updatedWorld))
    }

    const updateRoom = (id, update) =>{
        let unupdatedWorld = selectedWorld;
        let {nodes } = unupdatedWorld;
        let updatedNodes = {...nodes, [id]:update}
        let updatedWorld ={...selectedWorld, nodes:updatedNodes}
        dispatch(updateSelectedWorld(updatedWorld))
    }

    const deleteRoom = (id)=>{
        let unupdatedWorld = selectedWorld;
        let {rooms, nodes } = unupdatedWorld;
        let updatedRooms = rooms.filter(room => id !== room);
        let updatedNodes = delete nodes[id];
        let updatedWorld ={...selectedWorld, rooms: updatedRooms, nodes:updatedNodes};
        dispatch(updateSelectedWorld(updatedWorld));
    }

    //CHARACTERS
    // Adds new Character to selectedWorld state
    const addCharacter = (char)=>{
        let unupdatedWorld = selectedWorld;
        let {agents, nodes } = unupdatedWorld;
        console.log("CHARACTER BEING ADDED DATA", char)
        let formattedAgentId = char.node_id;
        
        while(agents.indexOf(formattedAgentId)>=0){
            console.log("WHILE LOOP RUNNING",agents.indexOf(formattedAgentId)>=0);
            let splitFormattedAgentId = formattedAgentId.split("_");
            console.log("FORMATTEDID:  ", splitFormattedAgentId);
            let idNumber = splitFormattedAgentId[splitFormattedAgentId.length-1]
            console.log("idNumber:  ", idNumber);
            idNumber = (idNumber*1)+1;
            idNumber = idNumber.toString()
            console.log("idNumber+:  ", idNumber);
            splitFormattedAgentId[splitFormattedAgentId.length-1] = idNumber
            console.log("splitFormattedAgentId+:  ", splitFormattedAgentId);
            formattedAgentId = splitFormattedAgentId.join("_")
            console.log("FORMATTEDIDEND:  ", formattedAgentId);
        }
        let updatedCharacterData = {...char, node_id:formattedAgentId};
        let updatedAgents = [...agents, formattedAgentId];
        let updatedRoomData = {...selectedRoom, contained_nodes:{...selectedRoom.contained_nodes, [formattedAgentId]:{target_id: formattedAgentId}}}
        let updatedNodes = {...nodes, [formattedAgentId]:updatedCharacterData, [selectedRoom.node_id]: updatedRoomData}
        let updatedWorld ={...selectedWorld, agents: updatedAgents, nodes:updatedNodes}
        dispatch(updateSelectedWorld(updatedWorld))
    }
    //Updates Character in selectedWorld state
    const updateCharacter = (id, update) =>{
        let unupdatedWorld = selectedWorld;
        let {nodes } = unupdatedWorld;
        let updatedNodes = {...nodes, [id]:update}
        let updatedWorld ={...selectedWorld, nodes:updatedNodes}
        dispatch(updateSelectedWorld(updatedWorld))
    }
    //Removes Character from selectedWorld state
    const deleteCharacter = (id)=>{
        let unupdatedWorld = selectedWorld;
        let {agents, nodes } = unupdatedWorld;
        let updatedAgents = agents.filter(char => id !== char);
        let updatedNodes = delete nodes[id];
        let updatedWorld ={...selectedWorld, agents: updatedAgents, nodes:updatedNodes};
        dispatch(updateSelectedWorld(updatedWorld));
    }
    //OBJECTS
    const addObject = (obj)=>{
        let unupdatedWorld = selectedWorld;
        let {objects, nodes } = unupdatedWorld;
        let formattedObjectId = obj.node_id;
        while(objects.indexOf(formattedObjectId)>=0){
            console.log("WHILE LOOP RUNNING", objects.indexOf(formattedObjectId)>=0);
            let splitFormattedObjectId = formattedObjectId.split("_");
            console.log("FORMATTEDID:  ", splitFormattedObjectId);
            let idNumber = splitFormattedObjectId[splitFormattedObjectId.length-1]
            console.log("idNumber:  ", idNumber);
            idNumber = (idNumber*1)+1;
            idNumber = idNumber.toString()
            console.log("idNumber+:  ", idNumber);
            splitFormattedObjectId[splitFormattedObjectId.length-1] = idNumber
            console.log("splitFormattedObjectId+:  ", splitFormattedObjectId);
            formattedObjectId = splitFormattedObjectId.join("_")
            console.log("FORMATTEDIDEND:  ", formattedObjectId);
        }
        let updatedObjectData = {...obj, node_id:formattedObjectId, container_node:{target_id:selectedRoom.node_id}};
        let updatedObjects = [...objects, formattedObjectId]
        let updatedRoomData = {...selectedRoom, contained_nodes:{...selectedRoom.contained_nodes, [formattedObjectId]:{target_id: formattedObjectId}}}
        let updatedNodes = {...nodes, [formattedObjectId]:updatedObjectData, [selectedRoom.node_id]: updatedRoomData}
        let updatedWorld ={...selectedWorld, objects: updatedObjects, nodes:updatedNodes}
        dispatch(updateSelectedWorld(updatedWorld))
    }
    const updateObject = (id, update) =>{
        let unupdatedWorld = selectedWorld;
        let {nodes } = unupdatedWorld;
        let updatedNodes = {...nodes, [id]:update}
        let updatedWorld ={...selectedWorld, nodes:updatedNodes}
        dispatch(updateSelectedWorld(updatedWorld))
    }
    const deleteObject = (id)=>{
        let unupdatedWorld = selectedWorld;
        let {objects, nodes } = unupdatedWorld;
        let updatedObjects = objects.filter(obj => id !== obj);
        let updatedNodes = delete nodes[id];
        let updatedWorld ={...selectedWorld, objects: updatedObjects, nodes:updatedNodes};
        dispatch(updateSelectedWorld(updatedWorld));
    }

    /* ------ LOCAL STATE ------ */
    const [roomCharacters, setRoomCharacters] = useState([]);
    const [roomObjects, setRoomObjects] = useState([]);
    const [roomIsIndoors, setRoomIsIndoors]= useState(null)

    //UTILS
    // worldNodeSorter - Sorts the the different types of nodes in a world into arrays
    const worldNodeSorter = (world)=>{
        let CharacterNodes = [];
        let RoomNodes = [];
        let ObjectNodes = [];
        const {nodes} = world;
        const WorldNodeKeys = Object.keys(nodes);
        WorldNodeKeys.map((nodeKey)=>{
            let WorldNode = nodes[nodeKey];
            if(WorldNode.classes){
            let NodeClass = WorldNode.classes[0]
            switch(NodeClass) {
                case "agent":
                CharacterNodes.push(WorldNode);
                break;
                case "object":
                ObjectNodes.push(WorldNode);
                break;
                case "room":
                RoomNodes.push(WorldNode);
                break;
                default:
                break;
                }
            }
        })
        dispatch(updateRooms(RoomNodes))
        dispatch(updateObjects(ObjectNodes))
        dispatch(updateCharacters(CharacterNodes))
    }

    // Handler
    const WorldSaveHandler = ()=>{
        let worldUpdates = {...worldRooms, worldObjects, worldCharacters}
        let updatedWorld = {...selectedWorld, nodes: worldUpdates}
        dispatch(updateSelectedWorld(updatedWorld))
        updateWorldsDraft()
        console.log("WORLD SAVE UPDATE:", updatedWorld)
    }

    const handleClick = ()=>{

        history.push(`/editworld/${worldId}/details/map/rooms/${roomid}/`);
      }
    //CRUMBS
    // const crumbs= [{name:` Overview` , linkUrl:`/editworld/${worldId}/details`}, {name:` Map` , linkUrl:`/editworld/${worldId}/details/map`},  {name:` Room:  ${selectedRoom.name}` , linkUrl:`/editworld/${worldId}/details/map/rooms/${roomid}`}]
    //BUTTON COPY
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

    /* --- LIFE CYCLE FUNCTIONS --- */
    useEffect(()=>{
        if(worldDrafts.length){
            worldDrafts.map((world) =>{
                const {id} = world;
                if(worldId == id){
                    dispatch(selectWorld(world))
                }
            })
        }
    },[worldDrafts])

    useEffect(()=>{
        if(selectedWorld){
            console.log("SELECTED WORLD:  ", selectedWorld)
            worldNodeSorter(selectedWorld)
        }
    },[selectedWorld])

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
        const {nodes} = selectedWorld;
        let CharacterNodes = [];
        let ObjectNodes = [];
            if(selectedRoom){
                const {contained_nodes}= selectedRoom;
                const roomContentNodesKeys = Object.keys(contained_nodes)
                roomContentNodesKeys.map((nodeKey)=>{
                    let WorldNode = nodes[nodeKey];
                    if(WorldNode.classes){
                    let NodeClass = WorldNode.classes[0]
                    switch(NodeClass) {
                        case "agent":
                        CharacterNodes.push(WorldNode);
                        break;
                        case "object":
                        ObjectNodes.push(WorldNode);
                        break;
                        default:
                        break;
                        }
                    }
                })
            }
            setRoomObjects(ObjectNodes)
            setRoomCharacters(CharacterNodes)
        }
    }, [selectedRoom])

    //CRUMBS
    const crumbs= [
        {name:` Overview` , linkUrl:`/editworld/${worldId}/${categories}`}, 
        {name:` Map` , linkUrl:`/editworld/${worldId}/${categories}/map`},
        {name:` ${roomid}` , linkUrl:`/editworld/${worldId}/${categories}/map/rooms/${roomid}`}
    ];

    return (
        <Container>
            <BreadCrumbs
                crumbs={crumbs}
            />
            {
            selectedRoom
            ?
            <>
            <Row>
                {/* <BreadCrumbs 
                    crumbs={crumbs}
                /> */}
            </Row>
            <Row>
                <Col>
                    <Row>
                        <TextInput
                            label="Room Name"
                            value={selectedRoom.name}
                        />
                    </Row>
                    <Row>
                        <GenerateForms 
                            label="Room Description:" 
                            value={selectedRoom.desc}
                        />
                    </Row>
                    <Row>
                        <TypeAheadTokenizerForm
                            formLabel="Room Objects"
                            tokenOptions={roomObjects}
                            worldId={worldId}
                            sectionName={"objects"}
                            roomId={selectedRoom.node_id}
                            defaultTokens={roomObjects}
                            onTokenAddition={addObject}
                            onTokenRemoval={deleteObject}
                        />
                    </Row>
                    <Row>
                        <TypeAheadTokenizerForm
                            formLabel="Character Objects"
                            tokenOptions={roomCharacters}
                            worldId={worldId}
                            sectionName={"characters"}
                            roomId={selectedRoom.node_id}
                            defaultTokens={roomCharacters}
                            onTokenAddition={addCharacter}
                            onTokenRemoval={deleteCharacter}
                        />
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
            </>
            :
            <div/>
            }
        </Container>
    );
}
export default RoomPage;