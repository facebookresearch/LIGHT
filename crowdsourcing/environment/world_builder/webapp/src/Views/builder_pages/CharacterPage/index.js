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
import Slider from "../../../components/world_builder/FormFields/Slider";
import BreadCrumbs from "../../../components/world_builder/BreadCrumbs";
import TypeAheadTokenizerForm from "../../../components/world_builder/FormFields/TypeAheadTokenizer";

const CharacterPage = ({
    api,
    builderRouterNavigate,
    currentLocation,
})=> {


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
    const worldRooms = useAppSelector((state) => state.worldRooms.worldRooms);
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
        builderRouterNavigate(newLocation)
    }
     //WORLD DRAFT
     const updateWorldDraft = ()=>{
        dispatch(setWorldDraft(selectedWorld))
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
    const [roomId, setRoomId] = useState("")
    const [charId, setCharId] = useState("")
    const [characterName, setCharacterName] = useState("");
    const [characterPrefix, setCharacterPrefix] = useState("");
    const [characterDesc, setCharacterDesc] = useState("");
    const [characterMotivation, setCharacterMotivation] = useState("")
    const [characterPersona, setCharacterPersona] = useState("");
    const [characterAggression, setCharacterAggression] = useState(0);
    const [characterSize, setCharacterSize] = useState(0);
    const [containedObjects, setContainedObjects] = useState([]);

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
        let updatedCharData = currentLocation;
        let updatedRoomData = taskRouterHistory[taskRouterHistory.length-1]
        setCharId(updatedCharData.id)
        setRoomId(updatedRoomData.id)
    },[currentLocation])

    useEffect(()=>{
        dispatch(updateSelectedWorld(worldDraft))
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
            console.log("CURRENT ROOM", currentRoom)
            dispatch(selectRoom(currentRoom))
        }
    },[selectedWorld])

    useEffect(()=>{
        if(selectedRoom){
            let {nodes}= selectedWorld
            let currentCharacter = nodes[charId]
            console.log("CURRENT CHARACTER", currentCharacter)
            dispatch(selectCharacter(currentCharacter))
        }
    },[selectedRoom])

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
            }
            setContainedObjects(ObjectNodes)
        }
    }, [selectedCharacter])

    //HANDLERS
    const CharacterNameChangeHandler = (e)=>{
        let updatedCharacterName = e.target.value;
        setCharacterName(updatedCharacterName)
        let updatedSelectedCharacter = {...selectedCharacter, name: updatedCharacterName }
        if(selectedCharacter){
            if(selectedCharacter.node_id){
                updateCharacter(selectedCharacter.node_id, updatedSelectedCharacter)
            }
        }
    }

    const CharacterDescChangeHandler = (e)=>{
        let updatedCharacterDesc = e.target.value;
        setCharacterDesc(updatedCharacterDesc)
        let updatedSelectedCharacter = {...selectedCharacter, desc: updatedCharacterDesc }
        if(selectedCharacter){
            if(selectedCharacter.node_id){
                updateCharacter(selectedCharacter.node_id, updatedSelectedCharacter)
            }
        }
    }

    const CharacterPersonaChangeHandler = (e)=>{
        let updatedCharacterPersona = e.target.value;
        setCharacterPersona(updatedCharacterPersona)
        let updatedSelectedCharacter = {...selectedCharacter, persona: updatedCharacterPersona }
        if(selectedCharacter){
            if(selectedCharacter.node_id){
                updateCharacter(selectedCharacter.node_id, updatedSelectedCharacter)
            }
        }
    }

    const CharacterPrefixChangeHandler = (e)=>{
        let updatedCharacterPrefix = e.target.value;
        setCharacterPrefix(updatedCharacterPrefix)
        let updatedSelectedCharacter = {...selectedCharacter, prefix: updatedCharacterPrefix }
        if(selectedCharacter){
            if(selectedCharacter.node_id){
                updateCharacter(selectedCharacter.node_id, updatedSelectedCharacter)
            }
        }
      }


    const CharacterSizeChangeHandler = (e)=>{
        let updatedCharacterSize = e.target.value;
        setCharacterSize(updatedCharacterSize);
        let updatedSelectedCharacter = {...selectedCharacter, size: updatedCharacterSize }
        if(selectedCharacter){
            if(selectedCharacter.node_id){
                updateCharacter(selectedCharacter.node_id, updatedSelectedCharacter)
            }
        }
    }

    const CharacterAggressionChangeHandler = (e)=>{
        let updatedCharacterAggression = e.target.value;
        setCharacterAggression(updatedCharacterAggression)
        let updatedSelectedCharacter = {...selectedCharacter, aggression: updatedCharacterAggression }
        if(selectedCharacter){
            if(selectedCharacter.node_id){
                updateCharacter(selectedCharacter.node_id, updatedSelectedCharacter)
            }
        }
    }

    //CRUMBS
    const crumbs= [...taskRouterHistory, currentLocation];

  return (
    <Container>
            <BreadCrumbs
                crumbs={crumbs}
            />
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
                        />
                    </Row>
                    <Row>
                        <GenerateForms
                            label="Character Persona:"
                            value={characterPersona}
                            changeHandler={CharacterPersonaChangeHandler}
                        />
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

                        />
                    </Col>
                    <Col>
                        <TextButton
                            text={"Delete Character"}

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
