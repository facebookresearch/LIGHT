/* REACT */
import React, {useState, useEffect} from 'react';
import { useParams, useRouteMatch, useHistory } from "react-router-dom";
/* REDUX */
import {useAppDispatch, useAppSelector} from '../../app/hooks';
/* ---- REDUCER ACTIONS ---- */
import { fetchWorlds, selectWorld } from "../../features/playerWorlds/playerworlds-slice.ts";
import { updateRooms} from "../../features/rooms/rooms-slice.ts";
import { updateObjects} from "../../features/objects/objects-slice.ts";
import { updateCharacters } from "../../features/characters/characters-slice.ts";
/* STYLES */

/* BOOTSTRAP COMPONENTS */
//LAYOUT
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
/* CUSTOM COMPONENTS */
import BreadCrumbs from "../../components/BreadCrumbs"
import WorldBuilderMap from "../../components/WorldBuilderMap2"
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

//Dummy Data
import DummyWorlds from "../../Copy/DummyData"

function WorldBuilderPage({ location }) { 
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
    const [mapBorders, setMapBorders] = useState({
        top: 2,
        bottom: -2,
        left: -2,
        right: 2
    })
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


    const handleClick = (roomId)=>{
        history.push(`/editworld/${worldId}/${categories}/map/rooms/${roomId}`);
    }


    //CRUMBS
    const crumbs= [{name:` Overview` , linkUrl:`/editworld/${worldId}/${categories}`}, {name:` Map` , linkUrl:`/editworld/${worldId}/${categories}/map`}]
    return (
        <div>
            <h2 data-testid="header" className="bp3-heading">
                World Builder
            </h2>
            <h3>World: {selectedWorld ? selectedWorld.name : null}</h3>
            {worldRooms.length ? worldRooms.map(room=><div>{room.name ? room.name : null}</div>) : null}
            {
            (worldRooms.length && mapBorders)
            ?
            <WorldBuilderMap
                worldRoomsData={worldRooms}
                worldBorders={mapBorders}
            />
            :
            null
            }
        </div>
    );
    }

//     const getManageOn = () => {
//     // Try and get if we should start with overlay or not
//     const loc = window.location.href;
//     const paramsIdx = loc.indexOf("?");
//     var initOverlay = false;
//     if (paramsIdx != -1) {
//         const params = loc.substring(paramsIdx + 1);
//         var res = params.split("=");
//         if (res[0] === "manage") {
//         initOverlay = res[1] == "true";
//         }
//     }
//     return initOverlay;
//     };

// function WorldBuilder({ upload, world }) {
//     const {name } = world;
//     const state = useWorldBuilder(upload);
//     const [advanced, setAdvanced] = React.useState(false);

//     const [isOverlayOpen, setIsOverlayOpen] = React.useState(getManageOn());
//     const world_name =
//         state.dimensions.name == null ? " " : state.dimensions.name;
//     const stateRef = React.useRef(state);
//     stateRef.current = state;
//     const TWO_MINUTES = 120000;

//     useEffect(() => {
//         const timer = setTimeout(function autosave() {
//         postAutosave(stateRef.current);
//         console.log("Autosaved!");
//         setTimeout(autosave, TWO_MINUTES);
//         }, TWO_MINUTES);
//         return () => clearTimeout(timer);
//     }, []);



//   return (
//     <div>
//         <h3>World: {name}</h3>

//     </div>
//   );
// }

export default WorldBuilderPage;