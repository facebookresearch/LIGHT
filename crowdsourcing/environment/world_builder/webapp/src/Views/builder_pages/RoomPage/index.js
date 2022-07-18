/* REACT */
import React, {useState, useEffect} from 'react';
/* REDUX */
import {useAppDispatch, useAppSelector} from '../../../app/hooks';
/* ---- REDUCER ACTIONS ---- */
import {setLoading} from "../../../features/loading/loading-slice";
import {setShowError, setErrorMessage} from "../../../features/errors/errors-slice";
import { updateSelectedWorld, setWorldDraft } from "../../../features/playerWorld/playerworld-slice.ts";
import { updateRooms, selectRoom} from "../../../features/rooms/rooms-slice.ts";
import { updateObjects} from "../../../features/objects/objects-slice.ts";
import { updateCharacters } from "../../../features/characters/characters-slice.ts";
import {updateTaskRouterHistory} from '../../../features/taskRouter/taskrouter-slice';
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
})=> {

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
        dispatch(setWorldDraft(selectedWorld));
    };
    //NAVIGATION
    const backStep = ()=>{
        let previousLoc =  taskRouterHistory[taskRouterHistory.length-1]
        console.log("history:  ", taskRouterHistory)
        let updatedHistory = taskRouterHistory.slice(0, taskRouterHistory.length-1);
        console.log("PREVIOUS LOC BACKSTEP:  ", previousLoc)
        builderRouterNavigate(previousLoc)
        dispatch(updateTaskRouterHistory(updatedHistory));
    };
    //GENERAL
    //Adds more than one node to currently selected room
    const addContent = (roomId, newNodes)=>{
        let {agents, objects, nodes } = selectedWorld;
        console.log("ROOM ID:  ", roomId)
        let unupdatedRoomData = nodes[roomId]
        console.log("ROOM DATA:  ", unupdatedRoomData)
        let unupdatedWorld = selectedWorld;
        let updatedNodes = {...nodes};
        let newObjects =[...agents];
        let newAgents = [...objects]
        let updatedContainedNodes = {...unupdatedRoomData.contained_nodes};
        newNodes.map((newNode)=>{
            let {classes} = newNode;
            let nodeType = classes[0];
            let formattedNewNode;
            let formattedNewNodetId;
            if(newNode.node_id){
                formattedNewNodetId = newNode.node_id;
                while((agents.indexOf(formattedNewNodetId)>=0) || objects.indexOf(formattedNewNodetId)>=0){
                    let splitformattedNewNodetId = formattedNewNodetId.split("_");
                    let idNumber = splitformattedNewNodetId[splitformattedNewNodetId.length-1];
                    idNumber = (idNumber*1)+1;
                    idNumber = idNumber.toString();
                    splitformattedNewNodetId[splitformattedNewNodetId.length-1] = idNumber;
                    formattedNewNodetId = splitformattedNewNodetId.join("_");
                };
            //
            }else{
                formattedNewNodetId = newNode.name +"_1" ;
            };
            if(nodeType === "agent"){
                newAgents.push(formattedNewNodetId);
            };
            if(nodeType === "object"){
                newObjects.push(formattedNewNodetId);
            };
            formattedNewNode = {...newNode, node_id:formattedNewNodetId , container_node:{target_id: roomId}};
            updatedContainedNodes = {...updatedContainedNodes, [formattedNewNodetId]:{target_id: formattedNewNodetId}};
            updatedNodes = {...updatedNodes, [formattedNewNodetId]:formattedNewNode};
        });
        let updatedRoomData = {...selectedRoom, contained_nodes: updatedContainedNodes};
        updatedNodes = {...updatedNodes, [roomId]: updatedRoomData};
        let updatedWorld ={...selectedWorld, agents: [...newAgents], objects:[...newObjects], nodes: updatedNodes};
        dispatch(updateSelectedWorld(updatedWorld));
    }

    //ROOMS
    const updateRoom = (id, update) =>{
        let unupdatedWorld = selectedWorld;
        let {nodes } = unupdatedWorld;
        let updatedNodes = {...nodes, [id]:update}
        let updatedWorld ={...selectedWorld, nodes:updatedNodes}
        dispatch(updateSelectedWorld(updatedWorld))
    }

    const deleteSelectedRoom = ()=>{
        let updatedWorld = containedNodesRemover(roomId)
        console.log("POST DELETION WORLD", updatedWorld)
        let updatedRooms = worldRooms.filter(room => roomId !== room);
        dispatch(setWorldDraft({...updatedWorld, rooms: updatedRooms}));
        backStep()
    }

    //CHARACTERS
    // Adds new Character to selectedWorld state
    const addCharacter = (char)=>{
        let unupdatedWorld = selectedWorld;
        let {agents, nodes } = unupdatedWorld;
        let formattedAgentId;
        //EXISTING CHARACTER
        if(char.node_id){
            formattedAgentId = char.node_id;
            while(agents.indexOf(formattedAgentId)>=0){
                let splitFormattedAgentId = formattedAgentId.split("_");
                let idNumber = splitFormattedAgentId[splitFormattedAgentId.length-1];
                if((typeof idNumber) === "Number"){
                    idNumber = (idNumber*1)+1;
                    idNumber = idNumber.toString();
                    splitFormattedAgentId[splitFormattedAgentId.length-1] = idNumber;
                    formattedAgentId = splitFormattedAgentId.join("_");
                }else{
                    formattedAgentId = char.name +"_1" ;
                }
            };
        //NEW CHARACTER
        }else{
            formattedAgentId = char.name +"_1" ;
        };
        let unupdatedRoomData = nodes[selectedRoom.node_id];
        let updatedCharacterData = {...char, node_id:formattedAgentId, container_node:{target_id: selectedRoom.node_id}};
        let updatedAgents = [...agents, formattedAgentId];
        let updatedContainedNodes = {...unupdatedRoomData.contained_nodes, [formattedAgentId]:{target_id: formattedAgentId}};
        let updatedRoomData = {...selectedRoom, contained_nodes: updatedContainedNodes};
        let updatedNodes = {...nodes, [formattedAgentId]:updatedCharacterData, [selectedRoom.node_id]: updatedRoomData};
        let updatedWorld ={...selectedWorld, agents: updatedAgents, nodes:updatedNodes};
        dispatch(updateSelectedWorld(updatedWorld));
    };

    //Removes Character from selectedWorld state
    const deleteCharacter = (id)=>{
        let unupdatedWorld = selectedWorld;
        let {agents, nodes } = unupdatedWorld;
        let updatedAgents = agents.filter(char => id !== char);
        let updatedNodes = {...nodes};
        delete updatedNodes[id];
        let unupdatedRoomData = {...nodes[selectedRoom.node_id]};
        let updatedContainedNodes = {...unupdatedRoomData.contained_nodes};
        delete updatedContainedNodes[id];
        let updatedRoomData = {...unupdatedRoomData, contained_nodes:updatedContainedNodes};
        updatedNodes = {...updatedNodes, [selectedRoom.node_id]:updatedRoomData};
        let updatedWorld ={...unupdatedWorld, agents: updatedAgents, nodes:updatedNodes};
        dispatch(updateSelectedWorld(updatedWorld));
    };

    //OBJECTS
    const addObject = (obj)=>{
        let unupdatedWorld = selectedWorld;
        let {objects, nodes } = unupdatedWorld;
        let formattedObjectId;
        //EXISTING OBJECT
        if(obj.node_id){
            formattedObjectId = obj.node_id;
            while(objects.indexOf(formattedObjectId)>=0){
                let splitFormattedObjectId = formattedObjectId.split("_");
                let idNumber = splitFormattedObjectId[splitFormattedObjectId.length-1];
                if((typeof idNumber) === "Number"){
                idNumber = (idNumber*1)+1;
                idNumber = idNumber.toString();
                splitFormattedObjectId[splitFormattedObjectId.length-1] = idNumber;
                formattedObjectId = splitFormattedObjectId.join("_");
                }else{
                    formattedObjectId = obj.name +"_1"
                }
            }
        } else {
        //NEW OBJECT
            formattedObjectId = obj.name +"_1"
        }
        let unupdatedRoomData = nodes[selectedRoom.node_id]
        let updatedObjectData = {...obj, node_id:formattedObjectId, container_node:{target_id:selectedRoom.node_id}};
        let updatedObjects = [...objects, formattedObjectId];
        let updatedContainedNodes = {...unupdatedRoomData.contained_nodes, [formattedObjectId]:{target_id: formattedObjectId}};
        let updatedRoomData = {...unupdatedRoomData, contained_nodes:updatedContainedNodes};
        let updatedNodes = {...nodes, [formattedObjectId]:updatedObjectData, [selectedRoom.node_id]: updatedRoomData};
        let updatedWorld ={...selectedWorld, objects: updatedObjects, nodes:updatedNodes};
        dispatch(updateSelectedWorld(updatedWorld));
    };

    const deleteObject = (id)=>{
        let unupdatedWorld = selectedWorld;
        let {objects, nodes } = unupdatedWorld;
        let updatedObjects = objects.filter(obj => id !== obj);
        let updatedNodes = {...nodes};
        delete updatedNodes[id];
        let unupdatedRoomData = {...nodes[selectedRoom.node_id]};
        let updatedContainedNodes = {...unupdatedRoomData.contained_nodes};
        delete updatedContainedNodes[id];
        let updatedRoomData = {...unupdatedRoomData, contained_nodes:updatedContainedNodes};
        updatedNodes = {...updatedNodes, [selectedRoom.node_id]:updatedRoomData};
        let updatedWorld ={...selectedWorld, objects: updatedObjects, nodes:updatedNodes};
        dispatch(updateSelectedWorld(updatedWorld));
    };


    /* ------ LOCAL STATE ------ */
    const [roomId, setRoomId] = useState(null);
    const [roomName, setRoomName] = useState("");
    const [roomDesc, setRoomDesc] = useState("");

    const [roomCharacters, setRoomCharacters] = useState([]);
    const [roomObjects, setRoomObjects] = useState([]);
    const [roomIsIndoors, setRoomIsIndoors]= useState(null);
    const [roomBrightness, setRoomBrightness] = useState(0);
    const [roomTemperature, setRoomTemperature] = useState(0);

    //UTILS
    //containedNodesRemover - helper function that handles deleteing any contained nodes in node being deleted
    const containedNodesRemover = (nodeId) => {
        let updatedWorld = selectedWorld;
        let {nodes} = updatedWorld;
        // nodeDigger - digs through nodes checking each one for contained node to generate a list of nodes to be removed from the world
        const nodeDigger = (id)=>{
          let unupdatedNode = nodes[id];
          let {classes, contained_nodes} = unupdatedNode;
          let containedNodes = contained_nodes;
          let containedNodesList = Object.keys(containedNodes);
          let updatedRemovalArray = [{nodeId: id, class: classes[0]}];
          if(!containedNodesList){
            return updatedRemovalArray;
          }else{
            while(containedNodesList.length){
                let currentNode = containedNodesList.pop();
                updatedRemovalArray=[...updatedRemovalArray, ...nodeDigger(currentNode)];
            };
            return updatedRemovalArray;
          };
        };
        let removalList = [];
        removalList = nodeDigger(nodeId);

        //Removal List is populated by nodeDigger function using the id of the deleted node then mapped through to remove nodes from the world
        removalList.map((removedNode)=>{
            let {agents, objects, rooms, nodes}= updatedWorld
          let removedNodeClass = removedNode.class;
          let removedNodeId = removedNode.nodeId;
            if(removedNodeClass ==="agent"){
              let updatedCharacters = agents.filter(char => removedNodeId !== char);
              updatedWorld = {...updatedWorld, agents: updatedCharacters};
            }else if(removedNodeClass ==="object" || removedNodeClass ==="container"){
              let updatedObjects = objects.filter(obj => removedNodeId !== obj);
              updatedWorld = {...updatedWorld, objects: updatedObjects};
            }else if(removedNodeClass ==="room"){
              let updatedRooms = rooms.filter(room => removedNodeId !== room);
              updatedWorld = {...updatedWorld, rooms: updatedRooms};
            }
            let updatedNodes = {...nodes};
            delete updatedNodes[removedNodeId];
            updatedWorld = {...updatedWorld, nodes: updatedNodes};
            console.log("updated post delete world", updatedWorld);
            dispatch(updateSelectedWorld(updatedWorld));
        });
        //
        console.log("UPDATED WORLD POST DIG AND DELETE",  updatedWorld)
        return updatedWorld;
    };
    // worldNodeSorter - Sorts the the different types of nodes in a world into arrays
    const worldNodeSorter = (world)=>{
        let CharacterNodes = [];
        let RoomNodes = [];
        let ObjectNodes = [];
        const {nodes} = world;
        const WorldNodeKeys = Object.keys(nodes);
        WorldNodeKeys.map((nodeKey)=>{
            let WorldNode = nodes[nodeKey];
            console.log("WORLD NODE:  ", WorldNode)
            if(WorldNode){
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
                     };
                }
            }
        });
        console.log(" NODE BREAKDOWN COR:  ", CharacterNodes, ObjectNodes, RoomNodes)
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
        setRoomId(currentLocation.id)
    },[worldDraft])

    useEffect(()=>{
        if(selectedWorld){
            console.log("SELECTED WORLD PRE SORTER:  ", selectedWorld)
            worldNodeSorter(selectedWorld)
        }
    },[selectedWorld])

    useEffect(()=>{
        if(selectedWorld){
            let {nodes}= selectedWorld;
            let currentRoom = nodes[roomId];
            if(currentRoom){
                dispatch(selectRoom(currentRoom));
            }
        }
    },[roomId, selectedWorld])

    useEffect(()=>{
        if(selectedWorld){
            const {nodes} = selectedWorld;
            let CharacterNodes = [];
            let ObjectNodes = [];
            if(selectedRoom){
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
                setRoomName(name);
                setRoomDesc(desc);
                setRoomIsIndoors(is_indoors);
                setRoomBrightness(brightness);
                setRoomTemperature(temperature);
                const roomContentNodesKeys = Object.keys(contained_nodes);
                roomContentNodesKeys.map((nodeKey)=>{
                    let worldNode = nodes[nodeKey];
                    if(worldNode){
                        if(worldNode.classes){
                            let NodeClass = worldNode.classes[0]
                            switch(NodeClass) {
                                case "agent":
                                    CharacterNodes.push(worldNode);
                                break;
                                case "object":
                                    ObjectNodes.push(worldNode);
                                break;
                                default:
                                break;
                            };
                        };
                    };
                });
                setRoomObjects(ObjectNodes);
                setRoomCharacters(CharacterNodes);
            };
        };
    }, [selectedRoom])

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

    //CRUMBS
    const crumbs= [...taskRouterHistory, currentLocation];

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
            <Row>
                <BreadCrumbs
                    crumbs={crumbs}
                />
            </Row>
            {
            selectedRoom
            ?
            <>
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
                            clickFunction={CommonSenseRoomContents}
                        />
                    </Row>
                    <Row>
                        <TypeAheadTokenizerForm
                            formLabel="Room Objects"
                            tokenOptions={roomObjects}
                            sectionName={"objects"}
                            containerId={selectedRoom.node_id}
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
                            containerId={selectedRoom.node_id}
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
                    clickFunction={updateWorldDraft}
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
