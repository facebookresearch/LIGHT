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
    api,
    builderRouterNavigate,
})=> {
    /* REDUX DISPATCH FUNCTION */
    const dispatch = useAppDispatch();
    /* ------ REDUX STATE ------ */ //Currently Taskrouter Redux Slice not working due to react version incompatiblity
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
    //Saves current SelectedWorld state to world draft and local storage
    const updateWorldDraft = ()=>{
        dispatch(setWorldDraft(selectedWorld));
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
            console.log("FORMATTED NEW NODE:  ", formattedNewNode)
            updatedNodes = {...updatedNodes, [formattedNewNodetId]:formattedNewNode};
        });
        let updatedRoomData = {...selectedRoom, contained_nodes: updatedContainedNodes};
        updatedNodes = {...nodes, [roomId]: updatedRoomData};
        let updatedWorld ={...selectedWorld, agents: [...newAgents], objects:[...newObjects], nodes:updatedNodes};
        dispatch(updateSelectedWorld(updatedWorld));
    }


   //ROOMS
   //Adds New Room to map and draft
    const addRoom = (room)=>{
        let unupdatedWorld = selectedWorld;
        let {rooms, nodes } = unupdatedWorld;
        //Room Id is initially generated from the new room's name a one added on.  It will iterate until it finds a unique key.
        let formattedRoomId = room.name.replaceAll(" ", "_") + "_1";
        while(rooms.indexOf(formattedRoomId)>=0){
            let splitFormattedRoomId = formattedRoomId.split("_")
            let idNumber = splitFormattedRoomId[splitFormattedRoomId.length-1];
            idNumber = idNumber++;
            splitFormattedRoomId[splitFormattedRoomId.length-1] = idNumber;
            formattedRoomId = splitFormattedRoomId.join("_");
        };
        let updatedRoomData = {...room, node_id:formattedRoomId};
        let updatedRooms = [...rooms, formattedRoomId];
        let updatedNodes = {...nodes, [formattedRoomId]:updatedRoomData};
        let updatedWorld ={...selectedWorld, rooms: updatedRooms, nodes:updatedNodes};
        dispatch(setWorldDraft(updatedWorld));
        dispatch(updateSelectedRoom(updatedRoomData));
    };

    //Updates room with any changes
    const updateRoom = (id, update) =>{
        let unupdatedWorld = selectedWorld;
        let {nodes } = unupdatedWorld;
        let updatedNodes = {...nodes, [id]:update};
        let updatedWorld ={...selectedWorld, nodes:updatedNodes};
        dispatch(updateSelectedWorld(updatedWorld));
    };

    //Updates room with any changes removes room nodes by ID and replaces them with a blank tile
    const deleteRoom = (id)=>{
        let unupdatedWorld = selectedWorld;
        let {rooms, nodes } = unupdatedWorld;
        let tileLocation = nodes[id].grid_location;
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
        delete updatedNodes[id];
        let updatedWorld ={...selectedWorld, rooms: updatedRooms, nodes:updatedNodes};
        dispatch(setWorldDraft(updatedWorld))
        dispatch(updateSelectedRoom(clearedTileData))
    }

    //Handles connecting rooms via clicking paths between the components.  This automatically updates the draft.  This function can only be invoked if there is an existing room on both ends of the path.
    const connectRooms = (
        primaryRoom,
        primaryRoomNeighbors,
        secondaryRoom,
        secondaryRoomNeighbors,
        pathAlignment
        )=>{
        let unupdatedWorld = selectedWorld;
        let {nodes} = unupdatedWorld;
        let primaryId = primaryRoom.node_id;
        let secondaryId = secondaryRoom.node_id;
        /*---- PRIMARY TILE UPDATE----*/
        let updatedRoomNode = primaryRoom;
        let updatedNeighbors = primaryRoomNeighbors;

        //PathDirection is text that is part of the room node and will state in which direction it's neighbor is connected
        let pathDirection
        if(pathAlignment==="vertical"){
            pathDirection= "the south";
        } else if(pathAlignment==="horizontal"){
            pathDirection= "the east";
        }else if(pathAlignment==="above"){
            pathDirection= "the floor beneath";
        } else if(pathAlignment==="below"){
            pathDirection= "the floor above";
        };

        //The primary tile's neighbor info template
        let neighborInfo = {
            examine_desc: null,
            label: `a path to ${pathDirection}`,
            locked_edge: null,
            target_id: secondaryRoom.node_id
        };

        /*---- SECONDARY TILE UPDATE----*/
        updatedNeighbors = {...primaryRoomNeighbors, [secondaryId]: neighborInfo};
        updatedRoomNode = {...primaryRoom, neighbors: updatedNeighbors};
        let updatedNeighborNode = secondaryRoom;
        let updatedNeighboringTileNeighbors = secondaryRoomNeighbors;

        let neighborPathDirection;
        if(pathAlignment==="vertical"){
            neighborPathDirection= "the north";
        } else if(pathAlignment==="horizontal"){
            neighborPathDirection= "the west";
        }else if(pathAlignment==="above"){
            neighborPathDirection= "the floor above";
        } else if(pathAlignment==="below"){
            neighborPathDirection= "the floor beneath";
        };

        //The secondary tile's neighbor info template
        let neighboringTileNeighborInfo = {
            examine_desc: null,
            label: `a path to ${neighborPathDirection}`,
            locked_edge: null,
            target_id: primaryRoom.node_id
        };

        updatedNeighboringTileNeighbors = {...secondaryRoomNeighbors, [primaryId]: neighboringTileNeighborInfo};
        updatedNeighborNode = {...secondaryRoom, neighbors:updatedNeighboringTileNeighbors};

        //Both Room nodes are updated and then update the world draft
        let updatedNodes = {...nodes, [updatedRoomNode.node_id]:updatedRoomNode, [updatedNeighborNode.node_id]: updatedNeighborNode};
        let updatedWorld = {...unupdatedWorld, nodes: updatedNodes};
        dispatch(setWorldDraft(updatedWorld));
    }

    //Handles disconnecting rooms via clicking paths between the components.  This automatically updates the draft.  This function can only be invoked if there is an existing room on both ends of the path.
    const disconnectRooms = (
        primaryRoom,
        primaryRoomNeighbors,
        secondaryRoom,
        secondaryRoomNeighbors,
        pathAlignment
        )=>{
        let unupdatedWorld = selectedWorld;
        let primaryId = primaryRoom.node_id;
        let secondaryId = secondaryRoom.node_id;

        /*---- PRIMARY TILE UPDATE----*/
        let updatedRoomNode = {...primaryRoom};
        let updatedNeighbors = {...primaryRoomNeighbors};
        delete updatedNeighbors[secondaryRoom.node_id];
        updatedRoomNode ={...primaryRoom, neighbors: updatedNeighbors};

        /*---- SECONDARY TILE UPDATE----*/
        let updatedNeighborNode = {...secondaryRoom};
        let updatedNeighboringTileNeighbors = {...secondaryRoomNeighbors};
        delete updatedNeighboringTileNeighbors[primaryId];
        updatedNeighborNode ={...updatedNeighborNode, neighbors: updatedNeighboringTileNeighbors};

        let {nodes} = unupdatedWorld;
        let updatedNodes = {...nodes, [primaryId]:updatedRoomNode, [secondaryId]: updatedNeighborNode};
        let updatedWorld = {...unupdatedWorld, nodes: updatedNodes};
        dispatch(setWorldDraft(updatedWorld))
    }

    /*---- MAP TRAVERSAL ----*/
    /*- FLOORS -*/
    const incrementFloorHandler = ()=> {
        const updatedFloor = floor+1;
        dispatch(updateFloor(updatedFloor));
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

    /*- MAP LAYOUT -*/
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
        let formattedAgentId;
        //EXISTING CHARACTER
        if(char.node_id){
            formattedAgentId = char.node_id;
            while(agents.indexOf(formattedAgentId)>=0){
                let splitFormattedAgentId = formattedAgentId.split("_");
                let idNumber = splitFormattedAgentId[splitFormattedAgentId.length-1];
                idNumber = (idNumber*1)+1;
                idNumber = idNumber.toString();
                splitFormattedAgentId[splitFormattedAgentId.length-1] = idNumber;
                formattedAgentId = splitFormattedAgentId.join("_");
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

    //Updates Character in selectedWorld state
    const updateCharacter = (id, update) =>{
        let unupdatedWorld = selectedWorld;
        let {nodes } = unupdatedWorld;
        let updatedNodes = {...nodes, [id]:update}
        let updatedWorld ={...selectedWorld, nodes:updatedNodes}
        dispatch(updateSelectedWorld(updatedWorld))
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
    }
    //OBJECTS
    // Adds new Object to selectedWorld state
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
                idNumber = (idNumber*1)+1;
                idNumber = idNumber.toString();
                splitFormattedObjectId[splitFormattedObjectId.length-1] = idNumber;
                formattedObjectId = splitFormattedObjectId.join("_");
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

    //Updates Object in selectedWorld state
    const updateObject = (id, update) =>{
        let unupdatedWorld = selectedWorld;
        let {nodes } = unupdatedWorld;
        let updatedNodes = {...nodes, [id]:update};
        let updatedWorld ={...selectedWorld, nodes:updatedNodes};
        dispatch(updateSelectedWorld(updatedWorld));
    };

    //Removes Object from selectedWorld state
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
    }

    /* ------ LOCAL STATE ------ */
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
        };

        roomNodes.map((roomNode)=>{
            let {grid_location} = roomNode;
            let x = grid_location[0]
            let y = grid_location[1]
            borders.top = borders.top > y ? borders.top : y;
            borders.bottom = borders.bottom < y ? borders.bottom : y;
            borders.right = borders.right > x ? borders.right : x;
            borders.left = borders.left < x ? borders.left : x;
        });
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
    };

    // worldNodeSorter sorts the the different types of nodes in a world into arrays
    const worldNodeSorter = (world)=>{
        let CharacterNodes = [];
        let RoomNodes = [];
        let ObjectNodes = [];
        const {nodes} = world;
        //sortFunction sorts array of nodes by name attribute alphabetically
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
        //Filters all world nodes into arrays by class (agent, object, room)
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
              };
            };
        });
        //Sorts each array alphabetically
        RoomNodes = RoomNodes.sort(sortFunction);
        ObjectNodes = ObjectNodes.sort(sortFunction);
        CharacterNodes = CharacterNodes.sort(sortFunction);
        //Updates each classes' state with updated arrays
        dispatch(updateRooms(RoomNodes));
        dispatch(updateObjects(ObjectNodes));
        dispatch(updateCharacters(CharacterNodes));
    };

    //fetchWorld
    // const fetchWorldCurrentWorld = ()=> {
    //     let unupdatedWorld  = JSON.parse(window.localStorage.getItem("taskWorld"))
    // }

    /* --- LIFE CYCLE FUNCTIONS --- */
    // Selects world from draft or world Data using params (worldId) *** discuss
    useEffect(()=>{
        if(worldDraft){
            window.localStorage.setItem("taskWorld", JSON.stringify(worldDraft));
            dispatch(updateSelectedWorld(worldDraft));
        };
    },[worldDraft]);

    // Uses worldNodeSorter helper function to break nodes into arrays and send them to respective redux slices.
    useEffect(()=>{
        if(selectedWorld){
            console.log("NODES BEING SORTED:  ", selectedWorld)
            worldNodeSorter(selectedWorld);
        };
      },[selectedWorld]);

    // Uses calculateMapBorders helper function to set borders that will be applied to Map to component data using room data
    useEffect(()=>{
        calculateMapBorders(worldRooms);
    },[worldRooms]);

    // Sets MapWidth and MapHeight state.
    useEffect(()=>{
        let {top, right, bottom, left} = mapBorders;
        let updatedMapWidthMultiplier = Math.abs(left) + right;
        let updatedMapHeightMultiplier = Math.abs(bottom) + top;
        let updatedMapWidth = updatedMapWidthMultiplier * -200;
        let updatedMapHeight = updatedMapHeightMultiplier * -200;
        console.log("HEIGHT AND MULT", updatedMapHeightMultiplier)
        console.log("HEIGHT", updatedMapHeight)
        const updatedDimensions = {
            width: updatedMapWidth,
            height: updatedMapHeight
        };
        console.log("UPDATED DIMENSIONS:", updatedDimensions)
        DimensionSetter(updatedDimensions);
    },[mapBorders]);

    // Handler
    //Saves current selectWorldState to draft and local storage
    const WorldSaveHandler = ()=>{
        updateWorldDraft();
    };

    //Closes side drawer
    const closeSidebar = ()=>{
        setMapSideBarOpen(false);
    };

    //Enters/exits color change mode.  User can click on existing rooms with color selected
    const ColorModeToggleHandler = ()=>{
        let updatedColorMode = !inColorMode ;
        setInColorMode(updatedColorMode);
    };

    //handleTileClick checks to see if map is in colorMode; if it is then it will color an existing tile otherwise it will select the room with the basic editor sidebar
    //*Note it will only color rooms that already exist.
    //*TODO: add pop up message when non existing room is clicked
    const handleTileClick= (room)=>{
        if(inColorMode){
            let {nodes} = selectedWorld;
            let updatedNode = nodes[room.node_id];
            if(updatedNode){
                updatedNode = {...updatedNode, color: selectedColor.hex};
                let updatedNodes = {...nodes, [room.node_id]:updatedNode};
                let updatedWorld = {...selectedWorld, nodes:updatedNodes};
                dispatch(setWorldDraft(updatedWorld))
            };
        }else{
            dispatch(selectRoom(room));
            setMapSideBarOpen(true);
        };
    };

    //ColorChangeHandler sets the color of the "brush" of the tile painter
    const ColorChangeHandler = (color) => {
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
                        addContent={addContent}
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
                        builderRouterNavigate={builderRouterNavigate}
                    />
                    :null
                }
                </SideBarDrawer>
            </div>
        </div>
    );
    }

export default WorldBuilderPage;
