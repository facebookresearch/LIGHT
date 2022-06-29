/* REACT */
import React, {useState, useEffect} from 'react';
/* REDUX */
import {useAppDispatch, useAppSelector} from '../../../app/hooks';
/* ---- REDUCER ACTIONS ---- */
import { updateSelectedWorld, setWorldDraft} from "../../../features/playerWorld/playerworld-slice.ts";
import { updateRooms, selectRoom} from "../../../features/rooms/rooms-slice.ts";
import { updateObjects} from "../../../features/objects/objects-slice.ts";
import { updateCharacters, selectCharacter } from "../../../features/characters/characters-slice.ts";
/* STYLES */
import './styles.css';
/* BOOTSTRAP COMPONENTS */
//LAYOUT
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
/* CUSTOM COMPONENTS */
import GenerateForms from "../../../components/world_builder/FormFields/GenerateForms";
import InlineTextInsertForm from "../../../components/world_builder/FormFields/InlineTextInsertForm";
import TextInput from "../../../components/world_builder/FormFields/TextInput";
import TextButton from "../../../components/world_builder/Buttons/TextButton";
import Button from 'react-bootstrap/Button';
import Slider from "../../../components/world_builder/FormFields/Slider";
import BreadCrumbs from "../../../components/world_builder/BreadCrumbs";
import TypeAheadTokenizerForm from "../../../components/world_builder/FormFields/TypeAheadTokenizer";

const CharacterPage = ({
    api,
    builderRouterNavigate,
})=> {
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

    /* REDUX DISPATCH FUNCTION */
    const dispatch = useAppDispatch();
    /* ------ REDUX STATE ------ */
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
    //TASKROUTER
    const navigateToLocation = (sectionName, nodeId)=>{
        let newLocation = {
            name: sectionName,
            id: nodeId
        };
        builderRouterNavigate(newLocation);
    };

     //WORLD DRAFT
     const updateWorldDraft = ()=>{
        dispatch(setWorldDraft(selectedWorld));
    };

    //GENERAL
    //Adds more than one node to currently selected character
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
            console.log("FORMATTED NEW NODE:  ", formattedNewNode)
            updatedNodes = {...updatedNodes, [formattedNewNodetId]:formattedNewNode};
            console.log("UPDATED NOTES IN ADD CONTENT FUNCTION IN MAPPING:  ", updatedNodes)
        });
        let updatedRoomData = {...selectedRoom, contained_nodes: updatedContainedNodes};
        updatedNodes = {...updatedNodes, [roomId]: updatedRoomData};
        console.log("UPDATED NOTES IN ADD CONTENT FUNCTION FINAL VERSION:  ", updatedNodes)
        let updatedWorld ={...selectedWorld, agents: [...newAgents], objects:[...newObjects], nodes: updatedNodes};
        dispatch(updateSelectedWorld(updatedWorld));
    };

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
    //Removes Current Character from selectedWorld state
    const deleteCharacter = (id)=>{
        console.log("DELETED ROOM ID:  ", id)
        let unupdatedWorld = selectedWorld;
        let {agents, nodes } = unupdatedWorld;
        let updatedAgents = agents.filter(char => id !== char);
        const updatedWorld = containedNodesRemover(id);
        dispatch(setWorldDraft({...updatedWorld, agents: updatedAgents}));
        builderRouterNavigate(taskRouterHistory[taskRouterHistory.length-2]);
    }
    //OBJECTS
    const addObject = (obj)=>{
        let unupdatedWorld = selectedWorld;
        let {objects, nodes } = unupdatedWorld;
        let formattedObjectId = obj.node_id;
        while(objects.indexOf(formattedObjectId)>=0){
            let splitFormattedObjectId = formattedObjectId.split("_");
            let idNumber = splitFormattedObjectId[splitFormattedObjectId.length-1];
            idNumber = (idNumber*1)+1;
            idNumber = idNumber.toString();
            splitFormattedObjectId[splitFormattedObjectId.length-1] = idNumber;
            formattedObjectId = splitFormattedObjectId.join("_");
        };
        let updatedObjectData = {...obj, node_id:formattedObjectId, container_node:{target_id:selectedRoom.node_id}};
        let updatedObjects = [...objects, formattedObjectId];
        let updatedRoomData = {...selectedRoom, contained_nodes:{...selectedRoom.contained_nodes, [formattedObjectId]:{target_id: formattedObjectId}}};
        let updatedNodes = {...nodes, [formattedObjectId]:updatedObjectData, [selectedRoom.node_id]: updatedRoomData};
        let updatedWorld ={...selectedWorld, objects: updatedObjects, nodes:updatedNodes};
        dispatch(updateSelectedWorld(updatedWorld));
    }
    const updateObject = (id, update) =>{
        let unupdatedWorld = selectedWorld;
        let {nodes } = unupdatedWorld;
        let updatedNodes = {...nodes, [id]:update};
        let updatedWorld ={...selectedWorld, nodes:updatedNodes};
        dispatch(updateSelectedWorld(updatedWorld));
    };


    const deleteObject = (id)=>{
        let unupdatedWorld = selectedWorld;
        let {objects, nodes } = unupdatedWorld;
        let updatedObjects = objects.filter(obj => id !== obj);
        let updatedNodes = delete nodes[id];
        let updatedWorld ={...selectedWorld, objects: updatedObjects, nodes:updatedNodes};
        dispatch(updateSelectedWorld(updatedWorld));
    }

    // COMMON SENSE DESCRIBE CHARACTER FUNCTION
    const CommonSenseDescribeCharacter = ()=>{
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
        suggestCharacterDescription({target_room, room_graph, target_id}).then((result) => {
            console.log("Finished describe character");
            console.log(result);
        })
    }

    // COMMON SENSE PERSONA CHARACTER FUNCTION
    const CommonSenseCharacterPersona = ()=>{
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
        suggestCharacterPersona({target_room, room_graph, target_id}).then((result) => {
            console.log("Finished persona character");
            console.log(result);
        })
    }

    // COMMON SENSE CONTENTS CHARACTER FUNCTION
    const CommonSenseCharacterContents = ()=>{
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
        suggestCharacterContents({target_room, room_graph, target_id}).then((result) => {
            console.log("Finished character contents");
            console.log(result);
            const newItems = result.new_items;
            addContent(target_room, newItems)
        })
    }

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


    //HANDLERS
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
        return updatedWorld;
    };

    //CRUMBS
    const crumbs= [...taskRouterHistory, currentLocation];
    /* --- LIFE CYCLE FUNCTIONS --- */

    useEffect(()=>{
        let updatedCharData = currentLocation;
        let updatedRoomData = taskRouterHistory[taskRouterHistory.length-1];
        console.log("CHAR ID:  ", updatedCharData)
        console.log("ROOM ID:  ", updatedRoomData)
        if(updatedCharData){
            setCharId(updatedCharData.id);
        }
        if(updatedRoomData){
            setRoomId(updatedRoomData.id);
        }
        console.log("WORLD DRAFT:  ", worldDraft);
        dispatch(updateSelectedWorld(worldDraft));
        console.log("CURRENT LOCATION USE EFFECT")
    },[currentLocation]);

    useEffect(()=>{
        dispatch(updateSelectedWorld(worldDraft))
        console.log("WORLD DRAFT USE EFFECT")
    },[worldDraft]);

    useEffect(()=>{
        if(selectedWorld){
            console.log("SELECTED WORLD:  ", selectedWorld)
            worldNodeSorter(selectedWorld)
        }
        console.log("SELECTED WORLD USE EFFECT 1")
    },[selectedWorld]);

    useEffect(()=>{
        if(roomId){
            let {nodes}= selectedWorld
            console.log("SELECTED WORLD:  ", selectedWorld);
            console.log("ROOM ID:  ", roomId)
            let currentRoom = nodes[roomId]
            console.log("CURRENT ROOM", currentRoom)
            if(currentRoom){
                dispatch(selectRoom(currentRoom))
            }
        }
        console.log("SELECTED ROOM USE EFFECT 2")
    },[roomId]);

    useEffect(()=>{
        if(charId){
            let {nodes}= selectedWorld
            let currentCharacter = nodes[charId]
            console.log("CURRENT CHARACTER", currentCharacter)
            if(currentCharacter){
                dispatch(selectCharacter(currentCharacter))
            };
        };
        console.log("SELECTED CHARACTER USE EFFECT")
    },[charId]);

    useEffect(()=>{
        if(selectedWorld){
        const {nodes} = selectedWorld;
        let ObjectNodes = [];
            if(selectedCharacter){
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
                setCharacterName(name);
                setCharacterDesc(desc);
                if(!name_prefix){
                    setCharacterPrefix("a");
                }else {
                    setCharacterPrefix(name_prefix);
                }
                setCharacterPersona(persona);
                setCharacterMotivation(motivation);
                setCharacterAggression(aggression);
                setCharacterSize(size);
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
                setContainedObjects(ObjectNodes)
            }
        }
        console.log("SELECTED CHARACTER USE EFFECT")
    }, [selectedCharacter])

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
                                generateName={"Generate Description"}
                                clickFunction={CommonSenseDescribeCharacter}
                            />
                        </Row>
                        <Row>
                            <GenerateForms
                                label="Character Persona:"
                                value={characterPersona}
                                changeHandler={CharacterPersonaChangeHandler}
                                generateName={"Generate Persona"}
                                clickFunction={CommonSenseCharacterPersona}
                            />
                        </Row>
                        <Row>
                            <Button onClick={CommonSenseCharacterContents} variant="primary">
                                Generate Character Contents
                            </Button>
                        </Row>
                        <Row>
                            <TypeAheadTokenizerForm
                                formLabel="Character Carrying"
                                tokenOptions={worldObjects}
                                sectionName={"objects"}
                                roomId={selectedRoom.node_id}
                                tokens={containedObjects}
                                tokenType={'objects'}
                                onTokenAddition={addObject}
                                onTokenRemoval={deleteObject}
                                builderRouterNavigate={builderRouterNavigate}
                            />
                        </Row>
                        <Row>
                            <TypeAheadTokenizerForm
                                formLabel="Wielding/Wearing"
                                tokenOptions={worldObjects}
                                sectionName={"objects"}
                                roomId={selectedRoom.node_id}
                                tokens={containedObjects}
                                tokenType={'objects'}
                                onTokenAddition={addObject}
                                onTokenRemoval={deleteObject}
                                builderRouterNavigate={builderRouterNavigate}
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
                                clickFunction={updateWorldDraft}
                            />
                        </Col>
                        <Col>
                            <TextButton
                                text={"Delete Character"}
                                clickFunction={()=>{deleteCharacter(charId)}}
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
