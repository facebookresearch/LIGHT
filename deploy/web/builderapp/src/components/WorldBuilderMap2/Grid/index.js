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
/* UTILS */
import {calculateMapBorders} from "../Utils"

const SIZE = 150;
const MARGIN = 24;

const Grid = ({
    dimensions
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
    const selectedRoom= useAppSelector((state) => state.worldRooms.selectedWorld);
    /* REDUX ACTIONS */
  
    /* ------ LOCAL STATE ------ */
    const [viewGrid, setViewGrid] = useState([])
    const [worldBorders, setWorldBorders] = useState(null)
    const [viewLoc, setViewLoc] = useState(
        {
            x: 0,
            y: 0
        }
    )
    const [viewFloor, setViewFloor] = useState(0)
    
    

    const formatGridData = () =>{
        const {x, y} = viewLoc;
        const tiles = []
        for (let i = y+2; i<= y-2; i--){
            for (let j = x-2; j <= x+2; j++) {
                let roomData = {
                    grid_location:[j, i, viewFloor]
                };
                viewGrid.map((roomNode)=>{
                    let {grid_location} = roomNode;
                    let xLoc = grid_location[0]
                    let yLoc = grid_location[1]
                    if(i==yLoc && j==xLoc){
                        roomData = roomNode
                    }
                })
                tiles.push(
                    <div
                      key={`${j}, ${i}`}
                      data-grid={{
                        x: j,
                        y: i,
                        w: 1,
                        h: 1,
    
                      }}
                    >
                        <Tile
                            x={j}
                            y={i}
                            tileStyle={{
                                width: SIZE,
                                height: SIZE,
                                maxWidth: SIZE,
                                maxHeight: SIZE,
                            }}
                            roomData={roomData}
                        />
                    </div>
                  );
            }
        }
        setViewGrid(tiles);
    }

    const filterByFloor = ()=>{
        const filteredRooms= worldRooms.filter((worldRoomNode)=>{
            let {grid_location} = worldRoomNode;
            let z = grid_location[2]
            return viewFloor == z
        })
        formatGridData(filteredRooms)
    }


    /* REACT LIFECYCLE */
    useEffect(()=>{
        let borders = calculateMapBorders(worldRooms)
        setWorldBorders(borders)
        filterByFloor()
    },[])


    return(
        <GridLayout
            cols={dimensions.width}
            rowHeight={SIZE}
            width={
            dimensions.width * SIZE +
            (dimensions.width + 1) * MARGIN
            }
            margin={[MARGIN, MARGIN]}
            isResizable={false}
            maxRows={dimensions.height}
            style={{
            width:
                dimensions.width * SIZE +
                (dimensions.width + 1) * MARGIN,
            }}
        >
            {viewGrid}
        </GridLayout>
    )
}
export default Grid;