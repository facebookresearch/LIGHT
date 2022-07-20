/* REACT */
import React, {useState, useEffect} from 'react';
/* REDUX */
import {useAppDispatch, useAppSelector} from '../../../app/hooks';
/* ---- REDUCER ACTIONS ---- */
//LOADING
import {setIsLoading} from "../../../features/loading/loading-slice";
//ERROR
import {setShowError, setErrorMessage} from "../../../features/errors/errors-slice";
//WORLD
import { updateSelectedWorld, setWorldDraft} from "../../../features/playerWorld/playerworld-slice.ts";
//ROOMS
import { updateRooms, selectRoom} from "../../../features/rooms/rooms-slice.ts";
//OBJECTS
import { updateObjects} from "../../../features/objects/objects-slice.ts";
//CHARACTERS
import { updateCharacters, selectCharacter } from "../../../features/characters/characters-slice.ts";
/* STYLES */
import './styles.css';
/* BOOTSTRAP COMPONENTS */
//LAYOUT
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
/* CUSTOM COMPONENTS */
//FORMS
import TypeAheadTokenizerForm from "../../../components/world_builder/FormFields/TypeAheadTokenizer";
import GenerateForms from "../../../components/world_builder/FormFields/GenerateForms";
import InlineTextInsertForm from "../../../components/world_builder/FormFields/InlineTextInsertForm";
import TextInput from "../../../components/world_builder/FormFields/TextInput";
//BUTTONS
import TextButton from "../../../components/world_builder/Buttons/TextButton";
import GenerateButton from "../../../components/world_builder/Buttons/GenerateButton";
//INPUT COMPONENTS
import Slider from "../../../components/world_builder/FormFields/Slider";
//BREADCRUMBS
import BreadCrumbs from "../../../components/world_builder/BreadCrumbs";

//CharacterPage - Advanced edit page for Selected Character
const CharacterPage = ({
    api,
    builderRouterNavigate,
})=> {

    //API
    let {
        getRoomAttributes,
        getRoomFill,
        suggestRoomContents,
        suggestCharacterContents,
        suggestCharacterDescription,
        suggestCharacterPersona,
        suggestObjectContents,
        getObjectFill,
        getCharacterFill,
    } = api;

    /* ------ LOCAL STATE ------ */
    const [roomId, setRoomId] = useState("");
    const [charId, setCharId] = useState("");
    const [characterName, setCharacterName] = useState("");
    const [characterPrefix, setCharacterPrefix] = useState("");
    const [characterDesc, setCharacterDesc] = useState("");
    const [characterMotivation, setCharacterMotivation] = useState("");
    const [characterPersona, setCharacterPersona] = useState("");
    const [characterAggression, setCharacterAggression] = useState(0);
    const [characterSize, setCharacterSize] = useState(0);
    const [containedObjects, setContainedObjects] = useState([]);
    const [carryObjects, setCarryObjects] = useState([]);
    const [wornObjects, setWornObjects] = useState([]);
    const [wieldedObjects, setWieldedObjects] = useState([]);

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
    const selectedWorld = useAppSelector((state) => state.playerWorld.selectedWorld);
    //ROOMS
    const selectedRoom = useAppSelector((state) => state.worldRooms.selectedRoom);
    //OBJECTS
    const worldObjects = useAppSelector((state) => state.worldObjects.worldObjects);
    //CHARACTERS
    const worldCharacters = useAppSelector((state) => state.worldCharacters.worldCharacters);
    const selectedCharacter = useAppSelector((state) => state.worldCharacters.selectedCharacter);
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

    //NAVIGATION
    //Goes to previous page
    const backStep = ()=>{
        let previousLoc =  taskRouterHistory[taskRouterHistory.length-1]
        let updatedHistory = taskRouterHistory.slice(0, taskRouterHistory.length-1);
        builderRouterNavigate(previousLoc);
        dispatch(updateTaskRouterHistory(updatedHistory));
    };

    //GENERAL
    //Adds more than one node to currently selected character
    const addContent = (charId, newNodes)=>{
        let unupdatedWorld = selectedWorld;
        let {objects, nodes } = unupdatedWorld;
        let unupdatedCharacterData = nodes[charId]
        let updatedNodes = {...nodes};
        let newObjects =[...objects];
        let updatedContainedNodes = {...unupdatedCharacterData.contained_nodes};
        newNodes.map((newNode)=>{
            let {classes} = newNode;
            let nodeType = classes[0];
            let formattedNewNode;
            let formattedNewNodetId;
            if(newNode.node_id){
                formattedNewNodetId = newNode.node_id;
                while( objects.indexOf(formattedNewNodetId)>=0){
                    let splitformattedNewNodetId = formattedNewNodetId.split("_");
                    let idNumber = splitformattedNewNodetId[splitformattedNewNodetId.length-1];
                    //if ID exists
                    if((typeof idNumber === "number") && (!Number.isNaN(idNumber))){
                        idNumber = parseInt(idNumber)
                        idNumber = idNumber+1;
                        idNumber = idNumber.toString();
                        splitFormattedObjectId[splitFormattedObjectId.length-1] = idNumber;
                        formattedObjectId = splitFormattedObjectId.join("_");
                    }else{ //if "IDNUMBER" ISN'T A NUMBER
                        formattedObjectId = newNode.name +"_1"
                    }
                };
            }else{
                //if ID Doesn't exist
                formattedNewNodetId = newNode.name +"_1" ;
            };
            if(nodeType === "object"){ //Updates Object Array
                newObjects.push(formattedNewNodetId);
            };
            formattedNewNode = {...newNode, node_id:formattedNewNodetId , container_node:{target_id: charId}};
            updatedContainedNodes = {...updatedContainedNodes, [formattedNewNodetId]:{target_id: formattedNewNodetId}};
            updatedNodes = {...updatedNodes, [formattedNewNodetId]:formattedNewNode};
        });
        let updatedCharacterData = {...selectedCharacter, contained_nodes: updatedContainedNodes};
        updatedNodes = {...updatedNodes, [charId]: updatedCharacterData};
        let updatedWorld ={...selectedWorld, objects:[...newObjects], nodes: updatedNodes};
        dispatch(updateSelectedWorld(updatedWorld));
    };

    //Updates Character in selectedWorld state
    const updateCharacter = (id, update) =>{
        let unupdatedWorld = selectedWorld;
        let {nodes } = unupdatedWorld;
        let updatedNodes = {...nodes, [id]:update};
        let updatedWorld ={...selectedWorld, nodes:updatedNodes};
        dispatch(updateSelectedWorld(updatedWorld));
    };

    //Removes Current Character from selectedWorld state
    const deleteCurrentCharacter = ()=>{
        let unupdatedWorld = selectedWorld;
        let {agents } = unupdatedWorld;
        let updatedAgents = agents.filter(char => charId !== char);
        const updatedWorld = containedNodesRemover(id);
        dispatch(setWorldDraft({...updatedWorld, agents: updatedAgents}));
        backStep();
    };

    //OBJECTS
    // Adds new Object to character inventory state
    const addObject = (obj, worn, wielded)=>{
        let unupdatedWorld = selectedWorld;
        let {objects, nodes } = unupdatedWorld;
        let formattedObjectId = obj.node_id;
        if(obj.node_id){ //EXISTING OBJECT
            while(objects.indexOf(formattedObjectId)>=0){
                let splitFormattedObjectId = formattedObjectId.split("_");
                let idNumber = parseInt(splitFormattedObjectId[splitFormattedObjectId.length-1]);
                if((typeof idNumber === "number") && (!Number.isNaN(idNumber))){
                    idNumber = parseInt(idNumber)
                    idNumber = idNumber+1;
                    idNumber = idNumber.toString();
                    splitFormattedObjectId[splitFormattedObjectId.length-1] = idNumber;
                    formattedObjectId = splitFormattedObjectId.join("_");
                }else{ //if "IDNUMBER" ISN'T A NUMBER
                    formattedObjectId = obj.name +"_1"
                }
            };
        }else { //NEW OBJECT
            formattedObjectId = obj.name +"_1"
        };
        let updatedObjectData = {...obj, node_id:formattedObjectId, container_node:{target_id: selectedCharacter.node_id}};
        if(worn){
            updatedObjectData = {...updatedObjectData, equipped: "worn", wearable:true};
        };
        if(wielded){
            updatedObjectData = {...updatedObjectData, equipped: "wield", wieldable:true};
        };
        let updatedObjects = [...objects, formattedObjectId];
        let updatedCharacterData = {...selectedCharacter, contained_nodes:{...selectedCharacter.contained_nodes, [formattedObjectId]:{target_id: formattedObjectId}}};
        let updatedNodes = {...nodes, [formattedObjectId]:updatedObjectData, [selectedCharacter.node_id]: updatedCharacterData};
        let updatedWorld ={...selectedWorld, objects: updatedObjects, nodes:updatedNodes};
        dispatch(updateSelectedWorld(updatedWorld));
    };

    //Removes Object from selectedWorld state
    const deleteObject = (id)=>{
        let unupdatedWorld = selectedWorld;
        let {objects } = unupdatedWorld;
        let {contained_nodes} = selectedCharacter
        let updatedContainedNodes = {...contained_nodes}
        delete updatedContainedNodes[id]
        let updatedCharacterData  = {...selectedCharacter, contained_nodes: updatedContainedNodes }
        let updatedObjects = objects.filter(obj => id !== obj);
        let updatedWorld = containedNodesRemover(id);
        let updatedNodes = {...updatedWorld.nodes, [updatedCharacterData.node_id]: updatedCharacterData}
        updatedWorld = {...updatedWorld, nodes:updatedNodes}
        dispatch(updateSelectedWorld({...updatedWorld, objects: updatedObjects}));
    };


    //UTILS
    //worldNodeSorter - filters nodes into their appropriate state and arrays upon changes to the selected or draft world
    const worldNodeSorter = (world)=>{
        let CharacterNodes = [];
        let RoomNodes = [];
        let ObjectNodes = [];
        const {nodes} = world;
        const WorldNodeKeys = Object.keys(nodes);
        WorldNodeKeys.map((nodeKey)=>{
            let WorldNode = nodes[nodeKey];
            if(WorldNode.classes){
            let NodeClass = WorldNode.classes[0];
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
            };
        });
        dispatch(updateRooms(RoomNodes));
        dispatch(updateObjects(ObjectNodes));
        dispatch(updateCharacters(CharacterNodes));
    };

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
        //Removal List is populated by nodeDigger function using the id of the deleted node then mapped through to remove nodes from the world
        let removalList = [];
        removalList = nodeDigger(nodeId);
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
            //Any changes during removal update the selectedWorld state as the removal list is mapped through
            dispatch(updateSelectedWorld(updatedWorld));
        });
        // The updated world is then returned for any additional changes that may need to be done
        return updatedWorld;
    };

    //Crumbs act as links to "pages" leading to the current page
    const crumbs= [...taskRouterHistory, currentLocation];

    //HANDLERS
    //WORLD DRAFT
    //updateWorldDraft - saves changes to currently selectedworld to world draft state and local storage
    const WorldSaveHandler = ()=>{
        dispatch(setWorldDraft(selectedWorld));
    };

    //TOKENIZER GEAR
    //the function that clicking a gear on the typeahead tokenizer invokes.  It saves the current worldState to the draft before navigating to the item or character's advanced page.
    const HandleBasicGearClick = (newLoc)=>{
        WorldSaveHandler()
        const {node_id} = selectedCharacter;
        let location = {
            name:"character",
            id: node_id
        };
        let updatedGearLocation = newLoc;
        const updatedRouterHistory = [...taskRouterHistory, currentLocation, location]
        dispatch(updateTaskRouterHistory(updatedRouterHistory));
        dispatch(setTaskRouterCurrentLocation(updatedGearLocation));
    }

    //FORM CHANGE HANDLER
    //CharacterNameChangeHandler handles any changes to character's name
    const CharacterNameChangeHandler = (e)=>{
        let updatedCharacterName = e.target.value;
        setCharacterName(updatedCharacterName);
        let updatedSelectedCharacter = {...selectedCharacter, name: updatedCharacterName };
        if(selectedCharacter){
            if(selectedCharacter.node_id){
                updateCharacter(selectedCharacter.node_id, updatedSelectedCharacter);
            };
        };
    };

    //CharacterNameChangeHandler handles any changes to character's description
    const CharacterDescChangeHandler = (e)=>{
        let updatedCharacterDesc = e.target.value;
        setCharacterDesc(updatedCharacterDesc);
        let updatedSelectedCharacter = {...selectedCharacter, desc: updatedCharacterDesc };
        if(selectedCharacter){
            if(selectedCharacter.node_id){
                updateCharacter(selectedCharacter.node_id, updatedSelectedCharacter);
            };
        };
    };

    //CharacterNameChangeHandler handles any changes to character's persona
    const CharacterPersonaChangeHandler = (e)=>{
        let updatedCharacterPersona = e.target.value;
        setCharacterPersona(updatedCharacterPersona);
        let updatedSelectedCharacter = {...selectedCharacter, persona: updatedCharacterPersona };
        if(selectedCharacter){
            if(selectedCharacter.node_id){
                updateCharacter(selectedCharacter.node_id, updatedSelectedCharacter);
            };
        };
    };

    //CharacterMotivationChangeHandler handles any changes to character's Motivation
    const CharacterMotivationChangeHandler = (e)=>{
        let updatedCharacterMotivation = e.target.value;
        setCharacterMotivation(updatedCharacterMotivation);
        let updatedSelectedCharacter = {...selectedCharacter, mission: updatedCharacterMotivation };
        if(selectedCharacter){
            if(selectedCharacter.node_id){
                updateCharacter(selectedCharacter.node_id, updatedSelectedCharacter);
            };
        };
    };

    //CharacterPrefixChangeHandler handles changes to character's prefix
    const CharacterPrefixChangeHandler = (e)=>{
        let updatedCharacterPrefix = e.target.value;
        setCharacterPrefix(updatedCharacterPrefix);
        let updatedSelectedCharacter = {...selectedCharacter, prefix: updatedCharacterPrefix };
        if(selectedCharacter){
            if(selectedCharacter.node_id){
                updateCharacter(selectedCharacter.node_id, updatedSelectedCharacter);
            };
        };
      };

    //CharacterSizeChangeHandler handles changes to character's size
    const CharacterSizeChangeHandler = (e)=>{
        let updatedCharacterSize = e.target.value;
        setCharacterSize(updatedCharacterSize);
        let updatedSelectedCharacter = {...selectedCharacter, size: updatedCharacterSize };
        if(selectedCharacter){
            if(selectedCharacter.node_id){
                updateCharacter(selectedCharacter.node_id, updatedSelectedCharacter);
            };
        };
    };

    //CharacterAggressionChangeHandler handles changes to character's aggression
    const CharacterAggressionChangeHandler = (e)=>{
        let updatedCharacterAggression = e.target.value;
        setCharacterAggression(updatedCharacterAggression);
        let updatedSelectedCharacter = {...selectedCharacter, aggression: updatedCharacterAggression };
        if(selectedCharacter){
            if(selectedCharacter.node_id){
                updateCharacter(selectedCharacter.node_id, updatedSelectedCharacter);
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
    //Generates Objects for Character
    const generateRoomContentButtonFunction = async ()=>{
        try{
            const payload = await CommonSenseCharacterContents();
            const {nodeId, data} = payload;
            addContent(nodeId, data);
            stopLoading();
        } catch (error) {
            stopLoading();
            console.log(error);
            errorHandler(error);
        };
    };

    //Generates description of character
    const generateCharacterDescButtonFunction = async ()=>{
        try{
            const payload = await CommonSenseDescribeCharacter();
            const {nodeId, data} = payload;
            updateCharacter(nodeId, data);
            stopLoading();
        } catch (error) {
            stopLoading();
            console.log(error);
            errorHandler(error);
        };
    };

    //Generates persona for character
    const generateCharacterPersonaButtonFunction = async ()=>{
        try{
            const payload = await CommonSenseCharacterPersona();
            const {nodeId, data} = payload;
            updateCharacter(nodeId, data);
            stopLoading();
        } catch (error) {
            stopLoading();
            console.log(error);
            errorHandler(error);
        };
    };

    //Generates motivation for character
    const generateCharacterMotivationButtonFunction = async ()=>{
        try{
            const payload = await CommonSenseCharacterMotivation();
            const {nodeId, data} = payload;
            updateCharacter(nodeId, data);
            stopLoading();
        } catch (error) {
            stopLoading();
            console.log(error);
            errorHandler(error);
        };
    };

    /* ------ END OF HANDLERS ------ */

    /* COMMON SENSE API INTERACTIONS */
    // COMMON SENSE CHARACTER DESCRIPTION GENERATION FUNCTION
    const CommonSenseDescribeCharacter = async ()=>{
        try{
            let target_room = selectedRoom['node_id'];
            let target_id = charId;
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
            const result = await suggestCharacterDescription({target_room, room_graph, target_id});
            console.log("Finished character description");
            const generatedData = result.updated_item;
            const updatedDesc = generatedData.desc;
            const updatedCharacter = {...selectedCharacter, desc:updatedDesc};
            console.log(updatedCharacter);
            const payload = {
                nodeId: target_id,
                data: updatedCharacter
            };
            return payload;
        } catch(error){
            stopLoading();
            errorHandler(error);
            throw error;
        };
    };

    // COMMON SENSE CHARACTER PERSONA GENERATION FUNCTION
    const CommonSenseCharacterPersona = async ()=>{
        try{
            let target_room = selectedRoom['node_id'];
            let target_id = charId;
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
            const result = await suggestCharacterPersona({target_room, room_graph, target_id});
            console.log("Finished character description");
            const generatedData = result.updated_item;
            const updatedpersona = generatedData.persona;
            const updatedCharacter = {...selectedCharacter, persona:updatedpersona};
            const payload = {
                nodeId: target_id,
                data: updatedCharacter
            };
            console.log(updatedCharacter);
            return payload;
        } catch(error){
            stopLoading();
            errorHandler(error);
            throw error;
        };
    };

    // COMMON SENSE CHARACTER MOTIVATION GENERATION FUNCTION
    const CommonSenseCharacterMotivation = async ()=>{
        try{
            let target_room = selectedRoom['node_id'];
            let target_id = charId;
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
            const result = await suggestCharacterMotivation({target_room, room_graph, target_id});
            console.log("Finished character description");
            const generatedData = result.updated_item;
            const updatedMotivation = generatedData.mission;
            const updatedCharacter = {...selectedCharacter, persona:updatedMotivation};
            const payload = {
                nodeId: target_id,
                data: updatedCharacter
            };
            console.log(updatedCharacter);
            return payload;
        } catch(error){
            stopLoading();
            errorHandler(error);
            throw error;
        };
    };

    // COMMON SENSE CHARACTER CONTENTS GENERATION FUNCTION
    const CommonSenseCharacterContents = async ()=>{
        try{
            startLoading()
            let target_room = selectedRoom['node_id'];
            let target_id = charId;
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
            const result = suggestCharacterContents({target_room, room_graph, target_id});
            console.log("Finished character contents", result);
            const newItems = result.new_items;
            const payload = {
                nodeId: target_id,
                data: newItems
            };
            return payload;
        } catch (error) {
            stopLoading();
            errorHandler(error);
            throw error;
        };
    };

    /* --- LIFE CYCLE FUNCTIONS --- */
    // Pulls params from current task router location anytime the currentLocation state changes
    useEffect(()=>{
        let updatedCharData = currentLocation;
        let updatedRoomData = taskRouterHistory[taskRouterHistory.length-1];
        if(updatedCharData){
            setCharId(updatedCharData.id);
        }
        if(updatedRoomData){
            setRoomId(updatedRoomData.id);
        }
        dispatch(updateSelectedWorld(worldDraft));
    },[currentLocation]);

    // Updates selectedWorld state upon change to worldDraft
    useEffect(()=>{
        dispatch(updateSelectedWorld(worldDraft))
    },[worldDraft]);

    // Updates all dependent Redux state upon change to selected world.
    useEffect(()=>{
        if(selectedWorld){
            worldNodeSorter(selectedWorld);
        }
    },[selectedWorld]);

    //Upon change to roomId state sets selectedRoom State
    useEffect(()=>{
        if(roomId){
            let {nodes}= selectedWorld;
            let currentRoom = nodes[roomId];
            if(currentRoom){
                dispatch(selectRoom(currentRoom));
            };
        };
    },[roomId]);

   //Upon change to charId state sets selectedCharacter State
    useEffect(()=>{
        if(charId){
            let {nodes}= selectedWorld;
            let currentCharacter = nodes[charId];
            if(currentCharacter){
                dispatch(selectCharacter(currentCharacter));
            };
        };
    },[charId, selectedWorld]);

    // Sets local state attributes in forms based on changes to selectedCharacter
    useEffect(()=>{
        if(selectedWorld){
        const {nodes} = selectedWorld;
        let objectNodes = [];
            if(selectedCharacter){
                //The attributes of a character are abstracted off the selectedCharacter state and then update the local state for each corresponding attribute
                const {
                    contain_size,
                    contained_nodes,
                    desc,
                    extra_desc,
                    motivation,
                    name,
                    name_prefix,
                    node_id,
                    persona,
                    prefix,
                    size,
                    aggression
                }= selectedCharacter;
                setCharacterName(name);//NAME
                setCharacterDesc(desc);//DESCRIPTION
                if(!name_prefix){
                    setCharacterPrefix("a");//PREFIX
                }else {
                    setCharacterPrefix(name_prefix);
                };
                setCharacterPersona(persona);//PERSONA
                setCharacterMotivation(motivation);//MOTIVATION
                setCharacterAggression(aggression);//AGGRESSION
                setCharacterSize(size);//SIZE
                const characterContentNodesKeys = Object.keys(contained_nodes);
                characterContentNodesKeys.map((nodeKey)=>{
                    let worldNode = nodes[nodeKey];
                    if(worldNode){
                        let {classes} = worldNode;
                        if(worldNode.classes){
                            let nodeClass = classes[0]
                            switch(nodeClass) {
                                case "object":
                                    objectNodes.push(worldNode);
                                break;
                                default:
                                break;
                                };
                        };
                    };
                });
                setContainedObjects(objectNodes);//CONTENT
            };
        };
    }, [selectedCharacter]);

    // Sorts objects in to local state for tokenizers upon changes to contained objects placing them into either carried, worn, or wielded object arrays
    useEffect(()=>{
        let updatedCarryObjects = [];
        let updatedWornObjects = [];
        let updatedWieldedObjects = []
        if(containedObjects.length){
            containedObjects.map(obj=>{
                if(obj.equipped){
                    if(obj.wearable){
                        updatedWornObjects.push(obj);
                    }
                    if(obj.wieldable){
                        updatedWieldedObjects.push(obj)
                    }
                }else{
                    updatedCarryObjects.push(obj);
                };
            });
        };
        setCarryObjects(updatedCarryObjects);
        setWornObjects(updatedWornObjects);
        setWieldedObjects(updatedWieldedObjects);
    }, [containedObjects]);

    return (
        <Container>
            <Row>
                <BreadCrumbs
                    crumbs={crumbs}
                />
            </Row>
                {
                selectedCharacter
                ?
                <>
                <Row>
                    <Col>
                        <Row>
                            <TextInput
                                label="Character Name"
                                value={characterName}
                                changeHandler={CharacterNameChangeHandler}
                            />
                        </Row>
                        <Row>
                            <GenerateForms
                                label="Character Description:"
                                value={characterDesc}
                                changeHandler={CharacterDescChangeHandler}
                                generateButtonLabel={"Generate Description"}
                                clickFunction={generateCharacterDescButtonFunction}
                            />
                        </Row>
                        <Row>
                            <GenerateForms
                                label="Character Persona:"
                                value={characterPersona}
                                changeHandler={CharacterPersonaChangeHandler}
                                generateButtonLabel={"Generate Persona"}
                                clickFunction={generateCharacterPersonaButtonFunction}
                            />
                        </Row>
                        <Row>
                            <GenerateForms
                                label="Motivation:"
                                value={characterMotivation}
                                changeHandler={CharacterMotivationChangeHandler}
                                generateButtonLabel={"Generate Motivation"}
                                clickFunction={generateCharacterMotivationButtonFunction}
                            />
                        </Row>
                        <Row>
                            <GenerateButton
                                label={"Generate Character Contents"}
                                clickFunction={generateRoomContentButtonFunction}
                                isloading={isLoading}
                            />
                        </Row>
                        <Row>
                            <TypeAheadTokenizerForm
                                formLabel="Character Carrying"
                                tokenOptions={worldObjects}
                                sectionName={"objects"}
                                containerId={selectedCharacter.node_id}
                                tokenType={'objects'}
                                objectWorn={false}
                                objectWielded={false}
                                tokens={carryObjects}
                                onTokenAddition={addObject}
                                onTokenRemoval={deleteObject}
                                builderRouterNavigate={HandleBasicGearClick}
                            />
                        </Row>
                        <Row>
                            <TypeAheadTokenizerForm
                                formLabel="Wearing"
                                tokenOptions={worldObjects}
                                sectionName={"objects"}
                                containerId={selectedCharacter.node_id}
                                tokenType={'objects'}
                                objectWorn={false}
                                objectWielded={false}
                                tokens={wornObjects}
                                onTokenAddition={(obj)=>addObject(obj, true, false)}
                                onTokenRemoval={deleteObject}
                                builderRouterNavigate={HandleBasicGearClick}
                            />
                        </Row>
                        <Row>
                            <TypeAheadTokenizerForm
                                formLabel="Wielding"
                                tokenOptions={worldObjects}
                                sectionName={"objects"}
                                containerId={selectedCharacter.node_id}
                                tokenType={'objects'}
                                objectWorn={false}
                                objectWielded={true}
                                tokens={wieldedObjects}
                                onTokenAddition={(obj)=>addObject(obj, false, true)}
                                onTokenRemoval={deleteObject}
                                builderRouterNavigate={HandleBasicGearClick}
                            />
                        </Row>
                    </Col>
                    <Col>
                        <Row>
                            <h5>In-Game appearance:</h5>
                        </Row>
                        <InlineTextInsertForm
                            formText={selectedCharacter.name}
                            value={characterPrefix}
                            changeHandler={CharacterPrefixChangeHandler}
                            textPlacement="after"
                        />
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
                                value={characterAggression}
                                min={0}
                                max={100}
                                changeHandler={CharacterAggressionChangeHandler}
                            />
                        </Row>
                        <Row>
                            <Slider
                                label="Size"
                                maxLabel="Big"
                                minLabel="Little"
                                value={characterSize}
                                min={0}
                                max={100}
                                changeHandler={CharacterSizeChangeHandler}
                            />
                        </Row>
                    </Col>
                    <Row>
                    <Col>
                        <Row>
                        <Col>
                            <TextButton
                                text={selectedCharacter.node_id ? "Save Changes" : "Create Character" }
                                clickFunction={WorldSaveHandler}
                            />
                        </Col>
                        <Col>
                            <TextButton
                                text={"Delete Character"}
                                clickFunction={deleteCurrentCharacter}
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
