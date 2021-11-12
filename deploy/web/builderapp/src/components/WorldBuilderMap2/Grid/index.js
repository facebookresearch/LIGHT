/* REACT */
import React, {useState, useEffect} from "react";
import { useParams, useRouteMatch, useHistory } from "react-router-dom";
/* REACT GRID LAYOUT*/
import GridLayout from "react-grid-layout";
/* REDUX */
import {useAppDispatch, useAppSelector} from '../../../app/hooks';
/* ---- REDUCER ACTIONS ---- */
import { fetchWorlds, selectWorld } from "../../../features/playerWorlds/playerworlds-slice.ts";

/* LODASH */
import { cloneDeep, isEmpty, isEqual } from "lodash";
/* BLUEPRINT JS COMPONENTS */
import { Button, Drawer, Classes } from "@blueprintjs/core";
/* CUSTOM COMPONENTS */
import Tile from "../Tile";

const SIZE = 150;
const MARGIN = 24;

const Grid = ({
    dimensions,
    viewLoc,
    borders
})=>{
    //REACT ROUTER
    const history = useHistory();
    let { worldId } = useParams();
    //let { path, url } = useRouteMatch();
    /* REDUX DISPATCH FUNCTION */
    const dispatch = useAppDispatch();
    /* ------ REDUX STATE ------ */
    //ROOMS
    const worldRooms = useAppSelector((state) => state.worldRooms.worldRooms);
    /* REDUX ACTIONS */
  
    /* ------ LOCAL STATE ------ */
    const [viewGrid, setViewGrid] = useState([])
    const [worldBorders, setWorldBorders] = useState(null)
    const [viewFloor, setViewFloor] = useState(0)
    
    

    const formatGridData = (rooms) =>{
        console.log("ROOMS", rooms)
        const {x, y} = viewLoc;
        const tiles = []
        for (let i = -2; i < 3; i++){
            for (let j = -2; j < 3; j++) {
                let roomData = {
                    grid_location:[j, i, viewFloor]
                };
                rooms.map((roomNode)=>{
                    console.log("room Nodes")
                    let {grid_location} = roomNode;
                    let RoomXPosition = grid_location[0]
                    let RoomYPosition = grid_location[1]
                    if(((i))==RoomYPosition -x && ((j))==RoomXPosition -y){
                        roomData = roomNode
                        console.log("ROOM DATA", roomData)
                    }
                })
                tiles.push(roomData);
            }
        }
        console.log("TILES", tiles)
        setViewGrid(tiles);
    }

    const filterByFloor = ()=>{
        const filteredRooms= worldRooms.filter((worldRoomNode)=>{
            let {grid_location} = worldRoomNode;
            let z = grid_location[2]
            console.log("VIEW FLOOR", viewFloor == z)
            return viewFloor == z
        })
        console.log("FILTERED", filteredRooms)
        formatGridData(filteredRooms)
    }


    /* REACT LIFECYCLE */
    useEffect(()=>{
        filterByFloor()
    },[])

    useEffect(()=>{
        filterByFloor()
    },[worldRooms])

    useEffect(()=>{
        filterByFloor()
    },[viewLoc])
    return(
        <GridLayout
            className="layout"
            cols={5}
            rowHeight={SIZE}
            width={
            dimensions.width * SIZE +
            (dimensions.width + 1) * MARGIN
            }
            isResizable={false}
            maxRows={5}

        >
            {
            viewGrid.length
            ?
            viewGrid.map(gridTile=> {

                let {grid_location} = gridTile;
                let x = grid_location[0]+2
                let y = grid_location[1]+2 
                let xLoc = viewLoc.x +x;
                let yLoc = viewLoc.y +y;
                return(
                <div
                    key={`${x}, ${y}`}
                    data-grid={{
                        x: x,
                        y: y,
                        w: 1,
                        h: 1,
                    }}
                >
                    <Tile
                        key={`${x}, ${y}`}
                        data-grid={{
                        x: x,
                        y: y,
                        w: 1,
                        h: 1,
                        }}
                        x={x}
                        y={y}
                        xPosition={xLoc}
                        yPosition={yLoc}
                        tileData={gridTile}
                    />
                </div>
                )
            })
            :
            null
        }
        </GridLayout>
    )
}
export default Grid;