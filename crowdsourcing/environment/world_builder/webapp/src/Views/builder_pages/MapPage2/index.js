/* REACT */
import React, {useState, useEffect} from 'react';
/* REDUX */
import {useAppDispatch, useAppSelector} from '../../../app/hooks';
/* ---- REDUCER ACTIONS ---- */
//WORLD
import { setWorldDraft, updateSelectedWorld } from "../../../features/playerWorld/playerworld-slice.ts";
//ROOMS
import { updateRooms, selectRoom} from "../../../features/rooms/rooms-slice.ts";
//MAP
import {updateFloor, updateDimensions, updatePosition, updateBorders} from "../../../features/map/map-slice"
//OBJECTS
import { updateObjects} from "../../../features/objects/objects-slice.ts";
//CHARACTERS
import { updateCharacters } from "../../../features/characters/characters-slice.ts";
/* STYLES */
import "./styles.css"
/* BOOTSTRAP COMPONENTS */
import Button from 'react-bootstrap/Button'
/* SKETCH PICKER COMPONENTS */
import { TwitterPicker } from 'react-color';
/* CUSTOM COMPONENTS */
import BreadCrumbs from "../../../components/world_builder/BreadCrumbs";
import NumberButtonInput from "../../../components/world_builder/NumberButtonInput";
import WorldBuilderMap from "../../../components/world_builder/WorldBuilderMap2";
import SideBarDrawer from "../../../components/world_builder/SideBarDrawer";
import BasicEditRoomBody from "./BasicEditRoomBody";
/* STYLES */
import "./styles.css";
import { updateSelectedRoom } from '../../../features/rooms/rooms-slice';

const WorldBuilderPage = ({
    api
})=> {
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
    //OBJECTS
    const worldObjects = useAppSelector((state) => state.worldObjects.worldObjects);
    //MAP
    const floor = useAppSelector((state) => state.map.floor);
    const mapBorders = useAppSelector((state) => state.map.mapBorders);
    const mapPosition = useAppSelector((state) => state.map.mapPosition);
    const mapWidth = useAppSelector((state) => state.map.mapWidth);
    const mapHeight = useAppSelector((state) => state.map.mapHeight);
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

        let formattedRoomId = room.name.replaceAll(" ", "_") + "_1";
        console.log("FORMATTED CREATE ROOM NAME:  ", formattedRoomId)
        while(rooms.indexOf(formattedRoomId)>=0){
            let splitFormattedRoomId = formattedRoomId.split("_")
            let idNumber = splitFormattedRoomId[splitFormattedRoomId.length-1]
            idNumber = idNumber++;
            splitFormattedRoomId[splitFormattedRoomId.length-1] = idNumber
            formattedRoomId = splitFormattedRoomId.join("_")
        }

        let updatedRoomData = {...room, node_id:formattedRoomId};
        console.log("UPDATED ROOM DATA:  ", updatedRoomData)
        let updatedRooms = [...rooms, formattedRoomId];
        console.log("UPDATED ROOMS UPON CREATION:  ", updatedRoomData)
        let updatedNodes = {...nodes, [formattedRoomId]:updatedRoomData};
        console.log("UPDATED NODES UPON CREATION:  ", updatedNodes)
        let updatedWorld ={...selectedWorld, rooms: updatedRooms, nodes:updatedNodes};
        console.log("UPDATED WORLDS UPON CREATION:  ", updatedWorld)
        dispatch(setWorldDraft(updatedWorld))
        dispatch(updateSelectedRoom(updatedRoomData))
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
        let tileLocation = nodes[id].grid_location
        let clearedTileData = {
            agent: false,
            classes: ["room"],
            contain_size: 0,
            contained_nodes: {},
            db_id: null,
            desc: "",
            extra_desc: "",
            name: "",
            name_prefix: "",
            names:[],
            neighbors: [],
            node_id: "",
            object: false,
            room: true,
            size:1,
            grid_location: tileLocation,
            surface_type: "",
        };
        let updatedRooms = rooms.filter(room => id !== room);
        let updatedNodes = {...nodes};
        delete updatedNodes[id]
        console.log("UPDAtED NODES DELETE:  ", updatedNodes)
        let updatedWorld ={...selectedWorld, rooms: updatedRooms, nodes:updatedNodes};
        dispatch(setWorldDraft(updatedWorld))
        dispatch(updateSelectedRoom(clearedTileData))
    }

    const connectRooms = (primaryRoom, primaryRoomNeighbors, secondaryRoom, secondaryRoomNeighbors, pathAlignment)=>{
        console.log("PRIMARY ROOM:  ", primaryRoom)
        console.log("PRIMARY NEIGHBORS:  ", primaryRoomNeighbors)
        console.log("SECONDARY ROOM:  ", secondaryRoom)
        console.log("SECONDARY NEIGHBORS:  ", secondaryRoomNeighbors)
        console.log("ALIGNMENT: ", pathAlignment)
        let unupdatedWorld = selectedWorld;
        let {nodes} = unupdatedWorld;
        let primaryId = primaryRoom.node_id;
        let secondaryId = secondaryRoom.node_id;

        let updatedRoomNode = primaryRoom;
        let updatedNeighbors = primaryRoomNeighbors;

        let pathDirection
        if(pathAlignment==="vertical"){
            pathDirection= "the south"
        } else if(pathAlignment==="horizontal"){
            pathDirection= "the east"
        }else if(pathAlignment==="above"){
            pathDirection= "the floor beneath"
        } else if(pathAlignment==="below"){
            pathDirection= "the floor above"
        }

        let neighborInfo = {
            examine_desc: null,
            label: `a path to ${pathDirection}`,
            locked_edge: null,
            target_id: secondaryRoom.node_id
        };

        updatedNeighbors = {...primaryRoomNeighbors, [secondaryId]: neighborInfo};
        console.log("NEIGHBOR POST UPDATE", updatedNeighbors)
        updatedRoomNode = {...primaryRoom, neighbors: updatedNeighbors};
        console.log("ROOM", primaryRoom.node_id, neighborInfo)
        let updatedNeighborNode = secondaryRoom;
        let updatedNeighboringTileNeighbors = secondaryRoomNeighbors;


        let neighborPathDirection
        if(pathAlignment==="vertical"){
            neighborPathDirection= "the north"
        } else if(pathAlignment==="horizontal"){
            neighborPathDirection= "the west"
        }else if(pathAlignment==="above"){
            neighborPathDirection= "the floor above"
        } else if(pathAlignment==="below"){
            neighborPathDirection= "the floor beneath"
        }

        let neighboringTileNeighborInfo = {
            examine_desc: null,
            label: `a path to ${neighborPathDirection}`,
            locked_edge: null,
            target_id: primaryRoom.node_id
        };
        updatedNeighboringTileNeighbors = {...secondaryRoomNeighbors, [primaryId]: neighboringTileNeighborInfo};
        console.log("NEIGHBOR NEIGHBORS POST UPDATE", updatedNeighboringTileNeighbors)
        updatedNeighborNode = {...secondaryRoom, neighbors:updatedNeighboringTileNeighbors};
        let updatedNodes = {...nodes, [updatedRoomNode.node_id]:updatedRoomNode, [updatedNeighborNode.node_id]: updatedNeighborNode};
        let updatedWorld = {...unupdatedWorld, nodes: updatedNodes};
        console.log("UPDATED WORLD CONNECT", updatedWorld)
        dispatch(setWorldDraft(updatedWorld))
    }

    const disconnectRooms = (primaryRoom, primaryRoomNeighbors, secondaryRoom, secondaryRoomNeighbors, pathAlignment)=>{
        console.log("PRIMARY ROOM:  ", primaryRoom)
        console.log("PRIMARY NEIGHBORS:  ", primaryRoomNeighbors)
        console.log("SECONDARY ROOM:  ", secondaryRoom)
        console.log("SECONDARY NEIGHBORS:  ", secondaryRoomNeighbors)
        console.log("ALIGNMENT: ", pathAlignment)
        let unupdatedWorld = selectedWorld;

        let primaryId = primaryRoom.node_id;
        let secondaryId = secondaryRoom.node_id;
        //Primary Room update
        let updatedRoomNode = {...primaryRoom};
        let updatedNeighbors = {...primaryRoomNeighbors};
        delete updatedNeighbors[secondaryRoom.node_id];
        console.log("POST DELETE NEIGHBORS:  ", updatedNeighbors)
        updatedRoomNode ={...primaryRoom, neighbors: updatedNeighbors};

        //Primary Room update
        let updatedNeighborNode = {...secondaryRoom};
        let updatedNeighboringTileNeighbors = {...secondaryRoomNeighbors};
        delete updatedNeighboringTileNeighbors[primaryId];
        console.log("POST DELETE NEIGHBORS NEIGHBOR:  ", updatedNeighboringTileNeighbors)
        updatedNeighborNode ={...updatedNeighborNode, neighbors: updatedNeighboringTileNeighbors};

        let {nodes} = unupdatedWorld;
        let updatedNodes = {...nodes, [primaryId]:updatedRoomNode, [secondaryId]: updatedNeighborNode};
        let updatedWorld = {...unupdatedWorld, nodes: updatedNodes};
        dispatch(setWorldDraft(updatedWorld))
    }
    //MAP
    const incrementFloorHandler = ()=> {
        const updatedFloor = floor+1;
        console.log(typeof updatedFloor, updatedFloor)
        dispatch(updateFloor(updatedFloor))
    }
    const decrementFloorHandler = ()=> {
        const updatedFloor = floor-1;
        console.log(typeof updatedFloor, updatedFloor)
        dispatch(updateFloor(updatedFloor))
    }
    const floorChangeHandler = (updatedFloor)=> {
        const newFloorValue = Number(updatedFloor)
        console.log(typeof newFloorValue, newFloorValue)
        dispatch(updateFloor(newFloorValue))
    }
    const DimensionSetter = (updatedDimensions)=>{
        dispatch(updateDimensions(updatedDimensions))
    }
    const BorderSetter = (updatedBorders)=>{
        dispatch(updateBorders(updatedBorders))
    }
    //CHARACTERS
    // Adds new Character to selectedWorld state
    const addCharacter = (char)=>{
        let unupdatedWorld = selectedWorld;
        let {agents, nodes } = unupdatedWorld;
        console.log("CHARACTER BEING ADDED DATA", char)
        let formattedAgentId
        if(char.node_id){
            formattedAgentId = char.node_id;

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
        }else{
            formattedAgentId = char.name +"_1"
        }
        let unupdatedRoomData = nodes[selectedRoom.node_id]
        let updatedCharacterData = {...char, node_id:formattedAgentId, container_node:{target_id: selectedRoom.node_id}};
        let updatedAgents = [...agents, formattedAgentId];
        let updatedContainedNodes = {...unupdatedRoomData.contained_nodes, [formattedAgentId]:{target_id: formattedAgentId}}
        console.log("UPDATED CONTAAINED NODES:  ", updatedContainedNodes )
        let updatedRoomData = {...selectedRoom, contained_nodes: updatedContainedNodes}
        console.log("UPDATE CHARACTERS ROOM DATA:  ", updatedRoomData)
        let updatedNodes = {...nodes, [formattedAgentId]:updatedCharacterData, [selectedRoom.node_id]: updatedRoomData}
        console.log("UPDATE CHARACTERS ROOM NODES:  ", updatedNodes)
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
        let updatedNodes = {...nodes}
        console.log("CHARACTER DELETION ID:  ", id)
        delete updatedNodes[id];
        console.log("POST CHARACTER DELETION UPDATED NODES:  ", updatedNodes)
        let unupdatedRoomData = {...nodes[selectedRoom.node_id]};
        let updatedContainedNodes = {...unupdatedRoomData.contained_nodes};
        delete updatedContainedNodes[id];
        let updatedRoomData = {...unupdatedRoomData, contained_nodes:updatedContainedNodes}
        updatedNodes = {...updatedNodes, [selectedRoom.node_id]:updatedRoomData}
        let updatedWorld ={...unupdatedWorld, agents: updatedAgents, nodes:updatedNodes};
        dispatch(updateSelectedWorld(updatedWorld));
    }
    //OBJECTS
    const addObject = (obj)=>{
        let unupdatedWorld = selectedWorld;
        let {objects, nodes } = unupdatedWorld;
        let formattedObjectId
        if(obj.node_id){

            formattedObjectId = obj.node_id;
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
        } else {
            formattedObjectId = obj.name +"_1"
        }
        let unupdatedRoomData = nodes[selectedRoom.node_id]
        let updatedObjectData = {...obj, node_id:formattedObjectId, container_node:{target_id:selectedRoom.node_id}};
        let updatedObjects = [...objects, formattedObjectId];
        let updatedContainedNodes = {...unupdatedRoomData.contained_nodes, [formattedObjectId]:{target_id: formattedObjectId}}
        console.log("UPDATED CONTAAINED NODES:  ", updatedContainedNodes )
        let updatedRoomData = {...unupdatedRoomData, contained_nodes:updatedContainedNodes}
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
        let updatedNodes = {...nodes}
        console.log("OBJECT DELETION ID:  ", id)
        delete updatedNodes[id];
        let unupdatedRoomData = {...nodes[selectedRoom.node_id]};
        let updatedContainedNodes = {...unupdatedRoomData.contained_nodes};
        delete updatedContainedNodes[id];
        let updatedRoomData = {...unupdatedRoomData, contained_nodes:updatedContainedNodes}
        updatedNodes = {...updatedNodes, [selectedRoom.node_id]:updatedRoomData}
        console.log("POST OBJECT DELETION UPDATED NODES:  ", updatedNodes)
        let updatedWorld ={...selectedWorld, objects: updatedObjects, nodes:updatedNodes};
        dispatch(updateSelectedWorld(updatedWorld));
    }

    // const SelectedWorldUpdateHandler = (update)=>{
    //     if(selectedWorld){
    //         let unupdatedWorld = selectedWorld;
    //         let {agents, nodes, objects, rooms} = selectedWorld;
    //         console.log("UPDATE", update)
    //     }
    // }
    /* ------ LOCAL STATE ------ */
    // const [floor, setFloor]= useState(0);
    // const [mapBorders, setMapBorders] = useState({
    //     top: 2,
    //     bottom: -2,
    //     left: -2,
    //     right: 2
    // });
    // const [mapWidth, setMapWidth]= useState(0);
    // const [mapHeight, setMapHeight] = useState(0);
    const [mapSideBarOpen, setMapSideBarOpen] = useState(false);
    const [inColorMode, setInColorMode] = useState(false);
    const [selectedColor, setSelectedColor] = useState("");

    //UTILS


    // calculateMapBorders- Calculates borders from array of roomnodes and sets border values.
    const calculateMapBorders = (roomNodes)=>{
        let borders = {
            top: Number.MIN_SAFE_INTEGER,
            bottom: Number.MAX_SAFE_INTEGER,
            left: Number.MAX_SAFE_INTEGER,
            right: Number.MIN_SAFE_INTEGER
        }
        roomNodes.map((roomNode)=>{
            let {grid_location} = roomNode;
            let x = grid_location[0]
            let y = grid_location[1]
            borders.top = borders.top > y ? borders.top : y;
            borders.bottom = borders.bottom < y ? borders.bottom : y;
            borders.right = borders.right > x ? borders.right : x;
            borders.left = borders.left < x ? borders.left : x;
        })
        // while((borders.top - borders.bottom)<3){
        //     borders.top = borders.top+1;
        //     borders.bottom = borders.bottom-1;
        // }
        // while((borders.right - borders.left)<3){
        //     borders.right = borders.right+1;
        //     borders.left = borders.left-1;
        // }
        console.log("BORDERS:  ", borders)
        return BorderSetter(borders);
    }

    // worldNodeSorter - Sorts the the different types of nodes in a world into arrays
    const worldNodeSorter = (world)=>{
        let CharacterNodes = [];
        let RoomNodes = [];
        let ObjectNodes = [];
        const {nodes} = world;
        const sortFunction = (a, b)=>{
            let firstItem=a.name.toLowerCase()
            let nextItem=b.name.toLowerCase();
            if (firstItem < nextItem) //sort string ascending
             return -1;
            if (firstItem > nextItem)
             return 1;
            return 0; //default return value (no sorting)
           };
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
        RoomNodes = RoomNodes.sort(sortFunction)
        ObjectNodes = ObjectNodes.sort(sortFunction)
        CharacterNodes = CharacterNodes.sort(sortFunction)
        dispatch(updateRooms(RoomNodes))
        dispatch(updateObjects(ObjectNodes))
        dispatch(updateCharacters(CharacterNodes))
    }

    const fetchWorldCurrentWorld = ()=> {
        let unupdatedWorld  = JSON.parse(window.localStorage.getItem("taskWorld"))

        dispatch(updateSelectedWorld(unupdatedWorld))
    }

    /* --- LIFE CYCLE FUNCTIONS --- */
    // Fetch world data from backend or from draft data if it exists.


    // Selects world from draft or world Data using params (worldId) *** discuss
    useEffect(()=>{
        if(worldDraft){
        console.log("WORLD DRAFT CHANGE DETECTED")
        window.localStorage.setItem("taskWorld", JSON.stringify(worldDraft))
        fetchWorldCurrentWorld()
        }
    },[worldDraft])

    // Uses worldNodeSorter helper function to break nodes into arrays and send them to respective redux slices.
    useEffect(()=>{
        if(selectedWorld){
            console.log("SELECTED WORLD:  ", selectedWorld)
            worldNodeSorter(selectedWorld)
        }
      },[selectedWorld])

    // Uses calculateMapBorders helper function to set borders that will be applied to Map to component data using room data
    useEffect(()=>{
        calculateMapBorders(worldRooms)
    },[worldRooms])

    // Sets MapWidth and MapHeight state.
    useEffect(()=>{
        let {top, right, bottom, left} = mapBorders;
        let updatedMapWidthMultiplier = Math.abs(left) + right;
        let updatedMapHeightMultiplier = Math.abs(bottom) + top;
        let updatedMapWidth = updatedMapWidthMultiplier * -200;
        let updatedMapHeight = updatedMapHeightMultiplier * -200;
        const updatedBorders = {
            width: updatedMapWidth,
            height: updatedMapHeight
        }
        DimensionSetter(updatedBorders);
    },[mapBorders])

    // Handler
    const WorldSaveHandler = ()=>{
        console.log("WORLD SAVE UPDATE:", selectedWorld)
        updateWorldDraft()
    }
    const closeSidebar = ()=>{
        setMapSideBarOpen(false)
    }

    const ColorModeToggleHandler = ()=>{
        let updatedColorMode = !inColorMode
        setInColorMode(updatedColorMode)
    }

    const handleTileClick= (room)=>{
        if(inColorMode){
            let {nodes} = selectedWorld;
            let updatedNode = nodes[room.node_id];
            if(updatedNode){
                updatedNode = {...updatedNode, color: selectedColor.hex};
                let updatedNodes = {...nodes, [room.node_id]:updatedNode};
                let updatedWorld = {...selectedWorld, nodes:updatedNodes};
                dispatch(setWorldDraft(updatedWorld))
            }
        }else{
            dispatch(selectRoom(room))
            setMapSideBarOpen(true)
        }
    }

    const ColorChangeHandler = (color) => {
        console.log("COLOR", color)
        setSelectedColor(color);
      };



    return (
        <div className="mappage-container">
            <div className="mappage-header">
                <h5>FLOOR</h5>
                <div className="toolbar-container">
                    <NumberButtonInput
                            incrementFunction={incrementFloorHandler}
                            decrementFunction={decrementFloorHandler}
                            changeFunction={(update)=>floorChangeHandler(update)}
                            value={floor}
                    />
                    <div className="colorbutton-container">
                        <Button
                            variant={inColorMode ? "primary":"secondary"}

                            onClick={ColorModeToggleHandler}
                        >
                            {inColorMode ? "COLOR MODE: ON": "COLOR MODE: OFF" }
                        </Button>
                    </div>
                    <div>
                        {
                            inColorMode ?
                            <div className="colorpicker-container">
                                <TwitterPicker
                                    triangle="left"
                                    onChangeComplete={ColorChangeHandler}
                                />
                            </div>
                            :
                            null
                        }
                    </div>
                </div>
            </div>
            <div className="mappage-body">
                {
                (selectedWorld && mapBorders)
                ?
                <WorldBuilderMap
                    worldData={selectedWorld}
                    worldRoomsData={worldRooms}
                    worldBorders={mapBorders}
                    tileClickFunction={handleTileClick}
                    floor={floor}
                    height={mapHeight}
                    width={mapWidth}
                    addRoom={addRoom}
                    updateRoom={updateRoom}
                    connectRooms={connectRooms}
                    disconnectRooms={disconnectRooms}
                />
                :
                null
                }
                <SideBarDrawer
                    showSideBar={mapSideBarOpen}
                    closeSideBarFunction={(closeSidebar)}
                    headerText={selectedRoom ? selectedRoom.node_id ? "EDIT ROOM" : "CREATE ROOM" : null}
                >{
                    selectedRoom
                    ?
                    <BasicEditRoomBody
                        currentRoom= {selectedRoom}
                        saveFunction = {WorldSaveHandler}
                        addRoom={addRoom}
                        updateRoom={updateRoom}
                        deleteRoom={deleteRoom}
                        addCharacter={addCharacter}
                        updateCharacter={updateCharacter}
                        deleteCharacter={deleteCharacter}
                        addObject={addObject}
                        updateObject={updateObject}
                        deleteObject={deleteObject}
                        api={api}
                    />
                    :null
                }
                </SideBarDrawer>
            </div>
        </div>
    );
    }

export default WorldBuilderPage;
