/* REACT */
import React, {useState, useEffect} from 'react';
/* REDUX */
import {useAppDispatch, useAppSelector} from '../../../app/hooks';
/* ---- REDUCER ACTIONS ---- */
//NAVIGATION
import {updateTaskRouterHistory, setTaskRouterCurrentLocation} from '../../../features/taskRouter/taskrouter-slice';
//LOADING
import {setIsLoading} from "../../../features/loading/loading-slice";
//ERROR
import {setShowError, setErrorMessage} from "../../../features/errors/errors-slice";
//WORLD
import { updateSelectedWorld, setWorldDraft } from "../../../features/playerWorld/playerworld-slice.ts";
//ROOMS
import { updateRooms, selectRoom} from "../../../features/rooms/rooms-slice.ts";
//OBJECTS
import { updateObjects} from "../../../features/objects/objects-slice.ts";
//CHARACTERS
import { updateCharacters } from "../../../features/characters/characters-slice.ts";
/* STYLES */
import './styles.css';
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
import GenerateButton from "../../../components/world_builder/Buttons/GenerateButton";
import BreadCrumbs from "../../../components/world_builder/BreadCrumbs";
import TypeAheadTokenizerForm from "../../../components/world_builder/FormFields/TypeAheadTokenizer";

//RoomPage - Advanced edit page for Selected Room
const RoomPage = ({
    api,
    builderRouterNavigate,
})=> {

    //API
    let {
        getRoomAttributes,
        getRoomFill,
        suggestRoomContents,
        suggestCharacterContents,
        suggestObjectContents,
        getObjectFill,
        getCharacterFill,
    } = api;

    /* ------ LOCAL STATE ------ */
    const [roomId, setRoomId] = useState(null);
    const [roomName, setRoomName] = useState("");
    const [roomDesc, setRoomDesc] = useState("");
    const [roomCharacters, setRoomCharacters] = useState([]);
    const [roomObjects, setRoomObjects] = useState([]);
    const [roomIsIndoors, setRoomIsIndoors]= useState(null);
    const [roomBrightness, setRoomBrightness] = useState(0);
    const [roomTemperature, setRoomTemperature] = useState(0);
    //REACT ROUTER
    /* REDUX DISPATCH FUNCTION */
    const dispatch = useAppDispatch();
    /* ------ REDUX STATE ------ */
    //LOADING
    const isLoading = useAppSelector((state) => state.loading.isLoading);
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
    //LOADING
    const startLoading = () =>{
        dispatch(setIsLoading(true));
    };
    const stopLoading = () =>{
        dispatch(setIsLoading(false));
    };
    //ERROR
    const showError = ()=>{
        dispatch(setShowError(true));
    };
    const setError = (errorMessage)=>{
        dispatch(setErrorMessage(errorMessage));
    };
    //WORLD DRAFT
    const updateWorldDraft = ()=>{
        dispatch(setWorldDraft(selectedWorld));
    };
    //NAVIGATION
    const backStep = ()=>{
        let previousLoc =  taskRouterHistory[taskRouterHistory.length-1]
        let updatedHistory = taskRouterHistory.slice(0, taskRouterHistory.length-1);
        builderRouterNavigate(previousLoc)
        dispatch(updateTaskRouterHistory(updatedHistory));
    };

    //GENERAL
    //Adds more than one node to currently selected room
    const addContent = (roomId, newNodes)=>{
        let {agents, objects, nodes } = selectedWorld;
        let unupdatedRoomData = nodes[roomId];
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
                    if((typeof idNumber === "number") && (!Number.isNaN(idNumber))){
                        idNumber = (idNumber*1)+1;
                        idNumber = idNumber.toString();
                        splitformattedNewNodetId[splitformattedNewNodetId.length-1] = idNumber;
                        formattedNewNodetId = splitformattedNewNodetId.join("_");
                    }else {
                        formattedNewNodetId = newNode.name+"_1" ;
                    };
                };
            }else{
                //NEW OBJECT
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
    };

    //ROOMS
    //Updates Room in selectedWorld state
    const updateRoom = (id, update) =>{
        let unupdatedWorld = selectedWorld;
        let {nodes } = unupdatedWorld;
        let updatedNodes = {...nodes, [id]:update};
        let updatedWorld ={...selectedWorld, nodes:updatedNodes};
        dispatch(updateSelectedWorld(updatedWorld));
    };

    //Removes SelectedRoom from selectedWorld state
    const deleteSelectedRoom = ()=>{
        let updatedWorld = containedNodesRemover(roomId)
        let updatedRooms = worldRooms.filter(room => roomId !== room);
        dispatch(setWorldDraft({...updatedWorld, rooms: updatedRooms}));
        backStep();
    };

    //CHARACTERS
    //Adds new Character to selectedWorld state
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

    /* ------ END OF REDUX ACTIONS ------ */

    /* UTILS */
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
            dispatch(updateSelectedWorld(updatedWorld));
        });
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
        dispatch(updateRooms(RoomNodes));
        dispatch(updateObjects(ObjectNodes));
        dispatch(updateCharacters(CharacterNodes));
    };

    /* --- LIFE CYCLE FUNCTIONS --- */
    //Updates currently selectedRoom any time worldDraft changes
    useEffect(()=>{
        dispatch(updateSelectedWorld(worldDraft));
        setRoomId(currentLocation.id);
    },[worldDraft]);

    //Updates currently selectedRoom any time selectedWorld changes
    useEffect(()=>{
        if(selectedWorld){
            worldNodeSorter(selectedWorld);
        };
    },[selectedWorld]);

    //Selects room based on any changes to roomId and updates currently selectedRoom anytime selectedWorld state changes
    useEffect(()=>{
        if(selectedWorld){
            let {nodes}= selectedWorld;
            let currentRoom = nodes[roomId];
            if(currentRoom){
                dispatch(selectRoom(currentRoom));
            }
        }
    },[roomId, selectedWorld]);

    //Upon any changes to selectedRoom selected fields in forms in local state will be updated by most recent selectedRoom data
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
    }, [selectedRoom]);

    //HANDLERS
    //FORM CHANGE HANDLER
    //RoomNameChangeHandler handles any changes to room's name
    const RoomNameChangeHandler = (e)=>{
        let updatedRoomName = e.target.value;
        setRoomName(updatedRoomName);
        let updatedSelectedRoom = {...selectedRoom, name: updatedRoomName };
        if(selectedRoom){
            if(selectedRoom.node_id){
                updateRoom(selectedRoom.node_id, updatedSelectedRoom);
            };
        };
    };
    //RoomDescChangeHandler handles any changes to room's description
    const RoomDescChangeHandler = (e)=>{
        let updatedRoomDesc = e.target.value;
        setRoomDesc(updatedRoomDesc);
        let updatedSelectedRoom = {...selectedRoom, desc: updatedRoomDesc };
        if(selectedRoom){
            if(selectedRoom.node_id){
                updateRoom(selectedRoom.node_id, updatedSelectedRoom);
            };
        };
    };

    //RoomIsIndoorsSetter sets room to indoors
    const RoomIsIndoorsSetter = ()=>{
        setRoomIsIndoors(true);
        let updatedSelectedRoom = {...selectedRoom, is_indoors: true };
        if(selectedRoom){
            if(selectedRoom.node_id){
                updateRoom(selectedRoom.node_id, updatedSelectedRoom);
            };
        };
    };

    //RoomIsIndoorsSetter sets room to outdoors
    const RoomIsOutdoorsSetter = ()=>{
        setRoomIsIndoors(false);
        let updatedSelectedRoom = {...selectedRoom, is_indoors: false };
        if(selectedRoom){
            if(selectedRoom.node_id){
                updateRoom(selectedRoom.node_id, updatedSelectedRoom);
            };
        };
    };

    //RoomBrightnessChangeHandler handles changes to room's brightness via slider value
    const RoomBrightnessChangeHandler = (e)=>{
        let updatedRoomBrightness = e.target.value;
        setRoomBrightness(updatedRoomBrightness);
        let updatedSelectedRoom = {...selectedRoom, brightness: updatedRoomBrightness }
        if(selectedRoom){
            if(selectedRoom.node_id){
                updateRoom(selectedRoom.node_id, updatedSelectedRoom);
            };
        };
    };

    //RoomTemperatureChangeHandler handles changes to room's temperature via slider value
    const RoomTemperatureChangeHandler = (e)=>{
        let updatedRoomTemperature = e.target.value;
        setRoomTemperature(updatedRoomTemperature);
        let updatedSelectedRoom = {...selectedRoom, temperature: updatedRoomTemperature };
        if(selectedRoom){
            if(selectedRoom.node_id){
                updateRoom(selectedRoom.node_id, updatedSelectedRoom);
            };
        };
    };

    //ERROR HANDLER
    //Shows and sets Error Message
    const errorHandler = (err)=>{
        setError(err);
        showError();
    };

    //GENERATE HANDLERS
    //Generates Characters and Objects for room
    const generateRoomContentButtonFunction = async ()=>{
        try{
            const payload = await CommonSenseRoomContents();
            const {nodeId, data} = payload;
            addContent(nodeId, data);
            stopLoading();
        } catch (error) {
            stopLoading();
            console.log(error);
            errorHandler(error);
        };
    };

    //Generates Description for SelectedRoom
    const generateRoomDescButtonFunction = async ()=>{
        try{
            const payload = await CommonSenseDescribeRoom();
            const {nodeId, data} = payload;
            updateRoom(nodeId, data);
            stopLoading();
        } catch (error) {
            stopLoading();
            console.log(error);
            errorHandler(error);
        };
    };

    /* ------ END OF HANDLERS ------ */

    /* COMMON SENSE API INTERACTIONS */
    // COMMON SENSE DESCRIBE ROOM GENERATION FUNCTION
    const CommonSenseDescribeRoom = async ()=>{
        try{
            startLoading()
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
            const result = await getRoomAttributes({target_room, room_graph});
            console.log("Finished describe room");
            console.log(result);
            const generatedData = result.updated_item;
            const updatedDesc = generatedData.desc;
            const updatedRoom = {...selectedRoom, desc:updatedDesc};
            const payload = {
                nodeId: target_room,
                data: updatedRoom
            };
            return payload
        } catch (error) {
            stopLoading()
            errorHandler(error)
            throw error;
        }
    }
    // COMMON SENSE FORM FUNCTION
    const CommonSenseRoomContents = async ()=>{
        try{
            startLoading()
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
            const result = await suggestRoomContents({target_room, room_graph})
            console.log("Finished Describe");
            console.log(result);
            const newItems = result.new_items;
            const payload = {
                nodeId: target_room,
                data: newItems
            };
            return payload;
        } catch (error) {
            stopLoading();
            errorHandler(error);
            throw error;
        };
    };

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
                            clickFunction={generateRoomDescButtonFunction}
                            generateButtonLabel={"Generate Room Description"}
                        />
                    </Row>
                    <Row>
                        <GenerateButton
                            clickFunction ={generateRoomContentButtonFunction}
                            label= {"SUGGEST ROOM CONTENTS"}
                            isLoading={isLoading}
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
                    text={selectedRoom.node_id ? "Save Changes" : "Create Room" }
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
