/* REACT */
import React, {useState, useEffect} from 'react';
import { useParams, useRouteMatch, useHistory } from "react-router-dom";
/* REDUX */
import {useAppDispatch, useAppSelector} from '../../app/hooks';
/* ---- REDUCER ACTIONS ---- */
import { fetchWorlds, updateSelectedWorld, selectWorld, setWorldDrafts} from "../../features/playerWorlds/playerworlds-slice.ts";
import { updateRooms, selectRoom} from "../../features/rooms/rooms-slice.ts";
import { updateObjects} from "../../features/objects/objects-slice.ts";
import { updateCharacters, selectCharacter } from "../../features/characters/characters-slice.ts";
/* STYLES */
import './styles.css';
/* BOOTSTRAP COMPONENTS */
//LAYOUT
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
/* CUSTOM COMPONENTS */
import GenerateForms from "../../components/FormFields/GenerateForms";
import TextInput from "../../components/FormFields/TextInput";
import TextButton from "../../components/Buttons/TextButton";
import ButtonToggle from "../../components/FormFields/ButtonToggle";
import Slider from "../../components/FormFields/Slider";
import BreadCrumbs from "../../components/BreadCrumbs";
import TypeAheadTokenizerForm from "../../components/FormFields/TypeAheadTokenizer";

const CharacterPage = ()=> {
    //REACT ROUTER
    const history = useHistory();
    let { worldId, roomid, charid } = useParams();
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
    const selectedCharacter = useAppSelector((state) => state.worldCharacters.selectedCharacter);
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
    const [characterObjects, setCharacterObjects] = useState([]);
    const [roomIsIndoors, setRoomIsIndoors]= useState(null)
    //UTILS
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
            console.log("CURRENT ROOM", currentRoom)
            dispatch(selectRoom(currentRoom))
        }
    },[selectedWorld])

    useEffect(()=>{
        if(selectedRoom){
            let {nodes}= selectedWorld
            let currentCharacter = nodes[charid]
            console.log("CURRENT CHARACTER", currentCharacter)
            dispatch(selectCharacter(currentCharacter))
        }
    },[selectedRoom])

    useEffect(()=>{
        if(selectedWorld){
        const {nodes} = selectedWorld;
        let ObjectNodes = [];
            if(selectedCharacter){
                const {contained_nodes}= selectedCharacter;
                const roomContentNodesKeys = Object.keys(contained_nodes)
                roomContentNodesKeys.map((nodeKey)=>{
                    let WorldNode = nodes[nodeKey];
                    if(WorldNode.classes){
                    let NodeClass = WorldNode.classes[0]
                    switch(NodeClass) {
                        case "object":
                        ObjectNodes.push(WorldNode);
                        break;
                        default:
                        break;
                        }
                    }
                })
            }
            setCharacterObjects(ObjectNodes)
        }
    }, [selectedCharacter])
  
//   //CRUMBS
//   const crumbs= [{name:` Overview` , linkUrl:`/editworld/${worldId}/details`}, {name:` Map` , linkUrl:`/editworld/${worldId}/details/map`},  {name:` Room:  ${selectedRoom.name}` , linkUrl:`/editworld/${worldId}/details/map/rooms/${roomid}`},{name:` Map` , linkUrl:`/editworld/${worldId}/details/map`},  {name:` Character:  ${selectedCharacter.name}` , linkUrl:`/editworld/${worldId}/details/map/rooms/${roomid}`} ]
  
  return (
    <Container>
            {
            selectedCharacter
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
                            label="Character Name"
                            value={selectedCharacter.name}
                        />
                    </Row>
                    <Row>
                        <GenerateForms 
                            label="Character Description:" 
                            value={selectedCharacter.desc}
                        />
                    </Row>
                    <Row>
                        <GenerateForms 
                            label="Character Persona:" 
                            value={selectedCharacter.persona}
                        />
                    </Row>
                    <Row>
                        <TypeAheadTokenizerForm
                            formLabel="Character Carrying"
                            tokenOptions={characterObjects}
                            worldId={worldId}
                            sectionName={"objects"}
                            roomId={selectedRoom.node_id}
                            defaultTokens={characterObjects}
                            onTokenAddition={addObject}
                            onTokenRemoval={deleteObject}
                        />
                    </Row>
                    <Row>
                        <TypeAheadTokenizerForm
                            formLabel="Wielding/Wearing"
                            tokenOptions={characterObjects}
                            worldId={worldId}
                            sectionName={"objects"}
                            roomId={selectedRoom.node_id}
                            defaultTokens={characterObjects}
                            onTokenAddition={addObject}
                            onTokenRemoval={deleteObject}
                        />
                    </Row>
                    <Row>
                        <TextInput
                            label="Motivation"
                            value={selectedCharacter.mission}
                        />
                    </Row>
                </Col>
                <Col>
                    <Row>
                        <h5>In-Game appearance:</h5>
                    </Row>
                    <Row>
                        <Col xs={1}>
                            <input
                                value={selectedCharacter.name_prefix}
                            />
                        </Col>
                        <Col xs={10}>
                        <h5>{selectedCharacter.name}</h5>
                        </Col>
                    </Row>
                    <Row>
                        <h5>Attributes</h5>
                    </Row>
                    <Row>

                    </Row>
                    <Row>
                        <Slider 
                            label="Aggression"
                            maxLabel="Angry"
                            minLabel="Peaceful"
                            value={selectedCharacter.aggression}
                            min={0}
                            max={100}
                        />
                    </Row>
                    <Row>
                        <Slider 
                            label="Size"
                            maxLabel="Big"
                            minLabel="Little"
                            value={selectedCharacter.size}
                            min={0}
                            max={100}
                        />
                    </Row>
                </Col>
                <Row>
                <Col>
                    <Row>
                    <Col>
                        <TextButton
                        text={selectedCharacter.node_id ? "Save Changes" : "Create Object" }

                        />
                    </Col>
                    <Col>
                        <TextButton
                        text={"Delete Object"}
                        
                        />
                    </Col>
                    </Row>
                </Col>
                <Col/>
                </Row>
            </Row>
            </>
            :
            <div/>
            }
    </Container>
  );
}

export default CharacterPage;