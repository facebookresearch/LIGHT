/* REACT */
import React, {useState, useEffect} from 'react';
import { useParams, useRouteMatch, useHistory } from "react-router-dom";
/* REDUX */
import {useAppDispatch, useAppSelector} from '../../app/hooks';
/* ---- REDUCER ACTIONS ---- */
import { fetchWorlds, selectWorld, setWorldDrafts, updateSelectedWorld } from "../../features/playerWorlds/playerworlds-slice.ts";
import { updateRooms, selectRoom} from "../../features/rooms/rooms-slice.ts";
import { updateObjects} from "../../features/objects/objects-slice.ts";
import { updateCharacters } from "../../features/characters/characters-slice.ts";
/* STYLES */
import "./styles.css"
/* BOOTSTRAP COMPONENTS */
import Button from 'react-bootstrap/Button'
/* SKETCH PICKER COMPONENTS */
import { SketchPicker } from 'react-color';
/* CUSTOM COMPONENTS */
import BreadCrumbs from "../../components/BreadCrumbs";
import NumberButtonInput from "../../components/NumberButtonInput";
import WorldBuilderMap from "../../components/WorldBuilderMap2";
import SideBarDrawer from "../../components/SideBarDrawer";
import BasicEditRoomBody from "./BasicEditRoomBody";
/* STYLES */
import "./styles.css";
//Dummy Data
import DummyWorlds from "../../Copy/DummyData";

const WorldBuilderPage = ()=> {
    let { worldId, categories } = useParams();
    /* REDUX DISPATCH FUNCTION */
    const dispatch = useAppDispatch();
    /* ------ REDUX STATE ------ */
    //WORLDS
    const worldDrafts = useAppSelector((state) => state.playerWorlds.worldDrafts);
    const selectedWorld = useAppSelector((state) => state.playerWorlds.selectedWorld);
    const worldRooms = useAppSelector((state) => state.worldRooms.worldRooms);
    const selectedRoom = useAppSelector((state) => state.worldRooms.selectedRoom);
    /* ------ REDUX ACTIONS ------ */
    const updateWorldsDraft = ()=>{
        let updatedWorlds = worldDrafts.map(world=> {
            if(world.id==worldId){
                return selectedWorld;
            }
            return world;
        })
        dispatch(setWorldDrafts(updatedWorlds))
    }

    /* ------ LOCAL STATE ------ */
    const [floor, setFloor]= useState(0); 
    const [mapBorders, setMapBorders] = useState({
        top: 2,
        bottom: -2,
        left: -2,
        right: 2
    });
    const [mapWidth, setMapWidth]= useState(0);
    const [mapHeight, setMapHeight] = useState(0);
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
            console.log("GRID LOC", grid_location)
            let x = grid_location[0]
            let y = grid_location[1]
            borders.top = borders.top > y ? borders.top : y;
            borders.bottom = borders.bottom < y ? borders.bottom : y;
            borders.right = borders.right > x ? borders.right : x;
            borders.left = borders.left < x ? borders.left : x;
        })
        // while((borders.top - borders.bottom)<3){
        //     borders.top = borders.top++;
        //     borders.bottom = borders.bottom--;
        // }
        // while((borders.right - borders.left)<3){
        //     borders.right = borders.right++;
        //     borders.left = borders.left--;
        // }
        console.log("BORDERS", borders)
        return setMapBorders(borders);
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
          })
          dispatch(updateRooms(RoomNodes))
          dispatch(updateObjects(ObjectNodes))
          dispatch(updateCharacters(CharacterNodes))
      }

    /* --- LIFE CYCLE FUNCTIONS --- */
    // Fetch world data from backend or from draft data if it exists.
    useEffect(()=>{
        dispatch(fetchWorlds(DummyWorlds))
    },[])
    
    // Selects world from draft or world Data using params (worldId) *** discuss
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

    // Uses worldNodeSorter helper function to break nodes into arrays and send them to respective redux slices.
    useEffect(()=>{
        if(selectedWorld){
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
        console.log("WIDTH", updatedMapWidth)
        console.log("HEIGHT", updatedMapHeight)
        setMapWidth(updatedMapWidth);
        setMapHeight(updatedMapHeight);
    },[mapBorders])

    // Handler
    const closeSidebar = ()=>{
        setMapSideBarOpen(false)
    }

    const ColorModeToggleHandler = ()=>{
        let updatedColorMode = !inColorMode
        setInColorMode(updatedColorMode)
    }

    const handleTileClick= (room)=>{
        console.log("CLICKED ROOM:  ", room)
        if(inColorMode){
            let {nodes} = selectedWorld;
            let updatedNode = nodes[room];
            if(updatedNode){
                updatedNode = {...updatedNode, color: selectedColor};
                let updatedNodes = {...nodes, [room.node_id]:updatedNode};
                let updatedWorld = {...selectedWorld, nodes:updatedNodes};
                dispatch(updateSelectedWorld(updatedWorld));
                updateWorldsDraft();
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

    //CRUMBS
    const crumbs= [
        {name:` Overview` , linkUrl:`/editworld/${worldId}/${categories}`}, 
        {name:` Map` , linkUrl:`/editworld/${worldId}/${categories}/map`}
    ]


    return (
        <div className="mappage-container">
            <div className="mappage-header">
                <BreadCrumbs
                    crumbs={crumbs}
                />
                <h5>FLOOR</h5>
                <div className="toolbar-container">
                    <NumberButtonInput
                            incrementFunction={()=>{setFloor(floor+1)}}
                            decrementFunction={()=>{setFloor(floor-1)}}
                            changeFunction={(update)=>setFloor(update)}
                            value={floor}
                    />
                    <div >
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
                            <SketchPicker 
                                onChangeComplete={ColorChangeHandler}
                            />
                            :
                            null
                        }
                    </div>
                </div>
            </div>
            <div className="mappage-body">
                {
                (worldRooms.length && mapBorders)
                ?
                <WorldBuilderMap
                    worldData={selectedWorld}
                    worldRoomsData={worldRooms}
                    worldBorders={mapBorders}
                    tileClickFunction={handleTileClick}
                    floor={floor}
                    height={mapHeight}
                    width={mapWidth}
                />
                :
                null
                }
                <SideBarDrawer
                    showSideBar={mapSideBarOpen}
                    closeSideBarFunction={(closeSidebar)}
                    headerText={selectedRoom ? selectedRoom.node_id ? "EDIT ROOM" : "CREATE ROOM" : null}
                >
                    <BasicEditRoomBody
                        worldId={worldId}
                        saveFunction = {updateWorldsDraft}
                    />
                </SideBarDrawer>
            </div>
        </div>
    );
    }

export default WorldBuilderPage;