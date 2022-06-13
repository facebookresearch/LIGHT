/* REACT */
import React, {useState, useEffect} from 'react';
import { useParams, useRouteMatch, useHistory } from "react-router-dom";
/* REDUX */
import {useAppDispatch, useAppSelector} from '../../../app/hooks';
/* ---- REDUCER ACTIONS ---- */
import { updateSelectedWorld, setWorldDraft } from "../../../features/playerWorld/playerworld-slice.ts";
import { updateRooms, selectRoom} from "../../../features/rooms/rooms-slice.ts";
import { updateObjects} from "../../../features/objects/objects-slice.ts";
import { updateCharacters } from "../../../features/characters/characters-slice.ts";
/* STYLES */
import './styles.css';
/* BOOTSTRAP COMPONENTS */
import Button from "react-bootstrap/Button"
//LAYOUT
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
/* CUSTOM COMPONENTS */
import TextInput from "../../../components/world_builder/FormFields/TextInput";
import TextButton from "../../../components/world_builder/Buttons/TextButton";
import ButtonToggle from "../../../components/world_builder/FormFields/ButtonToggle";
import Slider from "../../../components/world_builder/FormFields/Slider";
import GenerateForms from "../../../components/world_builder/FormFields/GenerateForms";
import BreadCrumbs from "../../../components/world_builder/BreadCrumbs";
import TypeAheadTokenizerForm from "../../../components/world_builder/FormFields/TypeAheadTokenizer";

const RoomPage = ({
    api,
    builderRouterNavigate,
    // currentLocation
})=> {

    /* ------ LOCAL STATE ------ */
    const [roomid, setRoomid] = useState(null);
    // //WORLD
    // // const [worldDraft, setWorldDraft] = useState(JSON.parse(window.localStorage.getItem("taskWorld")))
    // const [selectedWorld, setSelectedWorld] = useState(null);
    // //ROOMS
    // const [worldRooms, setWorldRooms] = useState([]);
    // const [selectedRoom, setSelectedRoom] = useState(null);
    // //OBJECTS
    // const [worldObjects, setWorldObjects] = useState([]);
    // //CHARACTERS
    // const [worldCharacters, setWorldCharacters] = useState([]);
    // //ACTIONS
    // const updateWorldDraft = (world)=>{
    //     window.localStorage.setItem("taskWorld", JSON.stringify(world));
    //     setWorldDraft(world)
    // }


    //REACT ROUTER
    /* REDUX DISPATCH FUNCTION */
    const dispatch = useAppDispatch();
    /* ------ REDUX STATE ------ */
    //TASKROUTER
    const currentLocation = useAppSelector((state) => state.taskRouter.currentLocation);
    const taskRouterHistory = useAppSelector((state) => state.taskRouter.taskRouterHistory);
    //WORLD
    const worldDraft = useAppSelector((state) => state.playerWorld.worldDraft);
    const selectedWorld = useAppSelector((state) => state.playerWorld.selectedWorld)
    //ROOMS
    const worldRooms = useAppSelector((state) => state.worldRooms.worldRooms);
    const selectedRoom = useAppSelector((state) => state.worldRooms.selectedRoom);
    //OBJECTS
    const worldObjects = useAppSelector((state) => state.worldObjects.worldObjects);
    //CHARACTERS
    const worldCharacters = useAppSelector((state) => state.worldCharacters.worldCharacters);
    /* ------ REDUX ACTIONS ------ */
    //WORLD DRAFT
    const updateWorldDraft = ()=>{
        dispatch(setWorldDraft(selectedWorld))
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

    const deleteSelectedRoom = ()=>{
        let updatedWorld = containedNodesRemover(roomid)
        console.log("POST DELETION WORLD", updatedWorld)
        // let {rooms, nodes } = updatedWorld;
        // let updatedRooms = rooms.filter(room => roomid !== room);
        // let updatedNodes ={...nodes};
        // delete updatedNodes[roomid];
        // updatedWorld ={...updatedWorld, rooms: updatedRooms, nodes:updatedNodes};
        dispatch(setWorldDraft(updatedWorld))
        builderRouterNavigate("/")
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
        dispatch(updateSelectedWorld(updatedWorld));
    }
    //Updates Character in selectedWorld state
    const updateCharacter = (id, update) =>{
        let unupdatedWorld = selectedWorld;
        let {nodes } = unupdatedWorld;
        let updatedNodes = {...nodes, [id]:update}
        let updatedWorld ={...selectedWorld, nodes:updatedNodes}
        dispatch(updateSelectedWorld(updatedWorld));
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
        dispatch(updateSelectedWorld(updatedWorld));
    }
    const updateObject = (id, update) =>{
        let unupdatedWorld = selectedWorld;
        let {nodes } = unupdatedWorld;
        let updatedNodes = {...nodes, [id]:update}
        let updatedWorld ={...selectedWorld, nodes:updatedNodes}
        dispatch(updateSelectedWorld(updatedWorld));
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
    const [roomName, setRoomName] = useState("");
    const [roomDesc, setRoomDesc] = useState("");

    const [roomCharacters, setRoomCharacters] = useState([]);
    const [roomObjects, setRoomObjects] = useState([]);
    const [roomIsIndoors, setRoomIsIndoors]= useState(null);
    const [roomBrightness, setRoomBrightness] = useState(0);
    const [roomTemperature, setRoomTemperature] = useState(0);

    //UTILS
    const containedNodesRemover = (nodeId)=>{

        console.log("RECURSIVE CONTAINED NODES REMOVER:  ", nodeId)

        let updatedWorld = selectedWorld;
        let {nodes} = updatedWorld;

        const nodeDigger = (id)=>{
          console.log("DIGGER ID AND ARRAY", id)
          let unupdatedNode = nodes[id];
          let {classes, contained_nodes} = unupdatedNode;
          let containedNodes = contained_nodes;
          let containedNodesList = Object.keys(containedNodes);
          console.log("containedNodesList", containedNodesList);
          let updatedRemovalArray = [{nodeId: id, class: classes[0]}];
          if(!containedNodesList){
            console.log("Non mapping REMOVAAL ARRAY", updatedRemovalArray);
            return updatedRemovalArray;
          }else{
            while(containedNodesList.length){
                let currentNode = containedNodesList.pop();
                updatedRemovalArray=[...updatedRemovalArray, ...nodeDigger(currentNode)];
            };
            return updatedRemovalArray;
          }
        }
        let removalList = [];
        removalList = nodeDigger(nodeId);

        removalList.map((removedNode, index)=>{
            let {agents, objects, rooms, nodes}= updatedWorld
            console.log("REMOVED NODES", removedNode, index)
          let removedNodeClass = removedNode.class;
          let removedNodeId = removedNode.nodeId
            if(removedNodeClass[0]==="agent"){
              let updatedCharacters = agents.filter(char => removedNodeId !== char);
              updatedWorld = {...updatedWorld, agents: updatedCharacters}
            }else if(removedNodeClass[0]==="object" || removedNodeClass[0]==="container"){
              let updatedObjects = objects.filter(obj => removedNodeId !== obj);
              updatedWorld = {...updatedWorld, objects: updatedObjects}
            }else if(removedNodeClass[0]==="room"){
              let updatedRooms = rooms.filter(room => removedNodeId !== room);
              updatedWorld = {...updatedWorld, rooms: updatedRooms}
            };
            let updatedNodes = {...nodes};
            delete updatedNodes[removedNodeId];
            console.log("updated post delete nodes", updatedNodes);
            updatedWorld = {...updatedWorld, nodes: updatedNodes};
        })
        console.log("UPDATED WORLD POST DIG AND DELETE",  updatedWorld);
        return updatedWorld;
      }
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
        });
        dispatch(updateRooms(RoomNodes));
        dispatch(updateObjects(ObjectNodes));
        dispatch(updateCharacters(CharacterNodes));
    }

    // Handler
    const WorldSaveHandler = ()=>{
        let worldUpdates = {...worldRooms, worldObjects, worldCharacters};
        let updatedWorld = {...selectedWorld, nodes: worldUpdates};
        dispatch(updateSelectedWorld(updatedWorld));
        dispatch(updateWorldDraft(updatedWorld));
        console.log("WORLD SAVE UPDATE:", updatedWorld);
    }

    /* --- LIFE CYCLE FUNCTIONS --- */
    useEffect(()=>{
        console.log("WORLD DRAFT IN ROOM PAGE:  ", worldDraft)
        dispatch(updateSelectedWorld(worldDraft));
    },[worldDraft])

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
            dispatch(selectRoom(currentRoom));
        }
        },[selectedWorld])

    useEffect(()=>{
        if(selectedWorld){
        const {nodes} = selectedWorld;
        let CharacterNodes = [];
        let ObjectNodes = [];
            if(selectedRoom){
                console.log("SELECTED ROOM DATA:  ", selectedRoom)
                const {
                    brightness,
                    contain_size,
                    contained_nodes,
                    desc,
                    extra_desc,
                    name,
                    name_prefix,
                    node_id,
                    is_indoors,
                    temperature
                }= selectedRoom;
                setRoomName(name)
                setRoomDesc(desc)
                setRoomIsIndoors(is_indoors)
                setRoomBrightness(brightness)
                setRoomTemperature(temperature)
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

    useEffect(()=>{
        let locationArray = currentLocation.split("/");
        console.log("LOCATION ARRAY IN ADVANCED ROOM PAGE:  ", locationArray)
        let currentRoomid = locationArray[locationArray.length-1];
        setRoomid(currentRoomid);

    }, [currentLocation])

    //HANDLERS
    const RoomNameChangeHandler = (e)=>{
        let updatedRoomName = e.target.value;
        setRoomName(updatedRoomName)
        let updatedSelectedRoom = {...selectedRoom, name: updatedRoomName }
        if(selectedRoom){
            if(selectedRoom.node_id){
                updateRoom(selectedRoom.node_id, updatedSelectedRoom)
            }
        }
    }

    const RoomDescChangeHandler = (e)=>{
        let updatedRoomDesc = e.target.value;
        setRoomDesc(updatedRoomDesc)
        let updatedSelectedRoom = {...selectedRoom, desc: updatedRoomDesc }
        if(selectedRoom){
            if(selectedRoom.node_id){
                updateRoom(selectedRoom.node_id, updatedSelectedRoom)
            }
        }
    }

    const RoomIsIndoorsSetter = ()=>{
        setRoomIsIndoors(true)
        let updatedSelectedRoom = {...selectedRoom, is_indoors: true }
        if(selectedRoom){
            if(selectedRoom.node_id){
                updateRoom(selectedRoom.node_id, updatedSelectedRoom)
            }
        }
    }

    const RoomIsOutdoorsSetter = ()=>{
        setRoomIsIndoors(false)
        let updatedSelectedRoom = {...selectedRoom, is_indoors: false }
        if(selectedRoom){
            if(selectedRoom.node_id){
                updateRoom(selectedRoom.node_id, updatedSelectedRoom)
            }
        }
    }

    const RoomBrightnessChangeHandler = (e)=>{
        let updatedRoomBrightness = e.target.value;
        setRoomBrightness(updatedRoomBrightness);
        let updatedSelectedRoom = {...selectedRoom, brightness: updatedRoomBrightness }
        if(selectedRoom){
            if(selectedRoom.node_id){
                updateRoom(selectedRoom.node_id, updatedSelectedRoom)
            }
        }
    }

    const RoomTemperatureChangeHandler = (e)=>{
        let updatedRoomTemperature = e.target.value;
        setRoomTemperature(updatedRoomTemperature)
        let updatedSelectedRoom = {...selectedRoom, temperature: updatedRoomTemperature }
        if(selectedRoom){
            if(selectedRoom.node_id){
                updateRoom(selectedRoom.node_id, updatedSelectedRoom)
            }
        }
    }

    //CRUMBS
//     const crumbs= [
// s
//         {name:` Map` , linkUrl:`/editworld/${worldId}/${categories}/map`},
//         {name:` ${roomid}` , linkUrl:`/editworld/${worldId}/${categories}/map/rooms/${roomid}`}
//     ];

    //BUTTON COPY
    const buttonOptions = [
        {
            name: "Indoors",
            value:1,
            clickFunction: ()=>RoomIsIndoorsSetter()
        },
        {
            name: "Outdoors",
            value:2,
            clickFunction: ()=>RoomIsOutdoorsSetter()
        },
    ]

    return (
        <Container>
            <Button onClick={()=>builderRouterNavigate("/")}> BACK </Button>
            {/* <BreadCrumbs
                crumbs={crumbs}
            /> */}
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
                            value={roomName}
                            changeHandler={RoomNameChangeHandler}
                        />
                    </Row>
                    <Row>
                        <GenerateForms
                            label="Room Description:"
                            value={roomDesc}
                            changeHandler={RoomDescChangeHandler}
                        />
                    </Row>
                    <Row>
                        <TypeAheadTokenizerForm
                            formLabel="Room Objects"
                            tokenOptions={roomObjects}
                            sectionName={"objects"}
                            roomId={selectedRoom.node_id}
                            tokens={roomObjects}
                            tokenType={'objects'}
                            onTokenAddition={addObject}
                            onTokenRemoval={deleteObject}
                            builderRouterNavigate={builderRouterNavigate}
                        />
                    </Row>
                    <Row>
                        <TypeAheadTokenizerForm
                            formLabel="Room Characters"
                            tokenOptions={roomCharacters}
                            sectionName={"characters"}
                            roomId={selectedRoom.node_id}
                            tokens={roomCharacters}
                            tokenType={'characters'}
                            onTokenAddition={addCharacter}
                            onTokenRemoval={deleteCharacter}
                            builderRouterNavigate={builderRouterNavigate}
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
                            value={roomBrightness}
                            min={0}
                            max={100}
                            changeHandler={RoomBrightnessChangeHandler}
                        />
                    </Row>
                    <Row>
                        <Slider
                            label="Temperature"
                            maxLabel="Hot"
                            minLabel="Cold"
                            value={roomTemperature}
                            min={0}
                            max={100}
                            changeHandler={RoomTemperatureChangeHandler}
                        />
                    </Row>
                </Col>
            </Row>
            <Row>
          <Col>
            <Row>
              <Col>
                <TextButton
                  text={selectedRoom.node_id ? "Save Changes" : "Create Object" }

                />
              </Col>
              <Col>
                <TextButton
                  text={"Delete Room"}
                  clickFunction={deleteSelectedRoom}
                />
              </Col>
            </Row>
          </Col>
          <Col/>
        </Row>
            </>
            :
            <div/>
            }
        </Container>
    );
}
export default RoomPage;
