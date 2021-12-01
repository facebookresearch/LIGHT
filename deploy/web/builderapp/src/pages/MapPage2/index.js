/* REACT */
import React, {useState, useEffect} from 'react';
import { useParams, useRouteMatch, useHistory } from "react-router-dom";
/* REDUX */
import {useAppDispatch, useAppSelector} from '../../app/hooks';
/* ---- REDUCER ACTIONS ---- */
import { fetchWorlds, selectWorld } from "../../features/playerWorlds/playerworlds-slice.ts";
import { updateRooms, selectRoom} from "../../features/rooms/rooms-slice.ts";
import { updateObjects} from "../../features/objects/objects-slice.ts";
import { updateCharacters } from "../../features/characters/characters-slice.ts";
/* STYLES */
import "./styles.css"
/* BOOTSTRAP COMPONENTS */
//LAYOUT
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
/* CUSTOM COMPONENTS */
import BreadCrumbs from "../../components/BreadCrumbs";
import NumberButtonInput from "../../components/NumberButtonInput";
import WorldBuilderMap from "../../components/WorldBuilderMap2";
import SideBarDrawer from "../../components/SideBarDrawer";
import BasicEditRoomBody from "./BasicEditRoomBody";
/* BLUEPRINT JS COMPONENTS */
import {
  NumericInput,
  InputGroup,
  ControlGroup,
  FormGroup,
  Tooltip,
  Position,
  Icon,
  Switch,
  Button,
  Intent,
} from "@blueprintjs/core";
/* STYLES */
import "./styles.css";
//Dummy Data
import DummyWorlds from "../../Copy/DummyData";

const WorldBuilderPage = ()=> { 
    //REACT ROUTER
    const history = useHistory();
    let { worldId, categories } = useParams();
    //let { path, url } = useRouteMatch();
    /* REDUX DISPATCH FUNCTION */
    const dispatch = useAppDispatch();
    /* ------ REDUX STATE ------ */
    //WORLDS
    const customWorlds = useAppSelector((state) => state.playerWorlds.customWorlds);
    const selectedWorld = useAppSelector((state) => state.playerWorlds.selectedWorld);
    const worldRooms = useAppSelector((state) => state.worldRooms.worldRooms)
    const selectedRoom = useAppSelector((state) => state.worldRooms.selectedRoom)
    /* ------ LOCAL STATE ------ */
    const [floor, setFloor]= useState(0)
    const [mapBorders, setMapBorders] = useState({
        top: 2,
        bottom: -2,
        left: -2,
        right: 2
    })
    const [mapSideBarOpen, setMapSideBarOpen] = useState(false);
    //UTILS
    const calculateMapBorders = (roomNodes)=>{
        let borders = {
            top: 2,
            bottom: -2,
            left: -2,
            right: 2
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
        return setMapBorders(borders);
    }

    const WorldNodeSorter = (world)=>{
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
        dispatch(fetchWorlds(DummyWorlds))
    },[])

    useEffect(()=>{
        if(customWorlds.length){
            customWorlds.map((world) =>{
                const {id} = world;
                if(worldId == id){
                    dispatch(selectWorld(world))
                }
            })
        }
    },[customWorlds])


    useEffect(()=>{
        if(selectedWorld){
          WorldNodeSorter(selectedWorld)
        }
      },[selectedWorld])

    useEffect(()=>{
        calculateMapBorders(worldRooms)
    },[worldRooms])

    //HANDLERS
    // const handleClick = (roomId)=>{
    //     history.push(`/editworld/${worldId}/${categories}/map/rooms/${roomId}`);
    // }

    const closeSidebar = ()=>{
        setMapSideBarOpen(false)
    }

    const handleTileClick= (room)=>{
        dispatch(selectRoom(room))
        setMapSideBarOpen(true)
    }

    //CRUMBS
    const crumbs= [{name:` Overview` , linkUrl:`/editworld/${worldId}/${categories}`}, {name:` Map` , linkUrl:`/editworld/${worldId}/${categories}/map`}]


    return (
        <div className="mappage-container">
            <div className="mappage-header">
                <BreadCrumbs
                    crumbs={crumbs}
                />
                <div className="toolbar-container">
                    <NumberButtonInput
                            incrementFunction={()=>{setFloor(floor+1)}}
                            decrementFunction={()=>{setFloor(floor-1)}}
                            changeFunction={(update)=>setFloor(update)}
                            value={floor}
                    />
                </div>
            </div>
            <div className="mappage-body">
                {
                (worldRooms.length && mapBorders)
                ?
                <WorldBuilderMap
                    worldRoomsData={worldRooms}
                    worldBorders={mapBorders}
                    tileClickFunction={handleTileClick}
                    floor={floor}
                />
                :
                null
                }
                <SideBarDrawer
                    showSideBar={mapSideBarOpen}
                    closeSideBarFunction={(closeSidebar)}
                    headerText="Edit Room"
                >
                    <BasicEditRoomBody

                    />
                </SideBarDrawer>
            </div>
        </div>
    );
    }

export default WorldBuilderPage;