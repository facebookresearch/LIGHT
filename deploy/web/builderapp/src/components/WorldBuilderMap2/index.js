/* REACT */
import React, {useEffect, useState} from 'react';
import { useParams, useRouteMatch, useHistory } from "react-router-dom";
/* REDUX */
import {useAppDispatch, useAppSelector} from '../../app/hooks';
/* CUSTOM COMPONENTS */
import Grid from "./Grid"
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

/* UTILS */
import {calculateMapBorders, gridDataGenerator} from "./Utils"


const STARTING_WIDTH = 5;
const STARTING_HEIGHT = 5;
const STARTING_FLOORS = 1;

const SIZE = 150;
const MARGIN = 24;

const WorldBuilderMap2 = ({worldRoomsData, worldBorders})=> {
    //REACT ROUTER
    const history = useHistory();
    let { worldId } = useParams();
    //let { path, url } = useRouteMatch();
    /* REDUX DISPATCH FUNCTION */
    const dispatch = useAppDispatch();
    /* ------ REDUX STATE ------ */
    //ROOMS
    // const worldRooms = useAppSelector((state) => state.worldRooms.worldRooms);
    // const selectedRoom= useAppSelector((state) => state.worldRooms.selectedWorld);
    /* ------ LOCAL STATE ------ */
    const [dimensions, setDimensions] = useState( 
        {
            name: null,
            height: STARTING_HEIGHT,
            width: STARTING_WIDTH,
            floors: STARTING_FLOORS,
        }
    );
    const [viewLoc, setViewLoc] = useState(
        {
            x: 0,
            y: 0
        }
    )
    const [gridData, setGridData] = useState(null)

    /* REACT LIFECYCLE */
    useEffect(()=>{
        let updatedGridData = gridDataGenerator(worldBorders, worldRoomsData, 0);
        console.log("GRID DATA OBJECT  ", updatedGridData)
        setGridData(updatedGridData)
    },[worldRoomsData])
    /* ------ Handlers ------ */
    const shiftView = (axis, amount)=>{
        let updatedView = {...viewLoc, [axis]: viewLoc[axis]+amount}
        console.log("updated view", updatedView)
        setViewLoc(updatedView)
    }
    return(
    <div
        style={{
          width:
            dimensions.width * SIZE +
            (dimensions.width + 1) * MARGIN +
            60,
          margin: "0 auto 75px auto",
          textAlign: "center",
        }}
    >
        <Button
            className="bp3-button"
            style={{
            width:
                dimensions.width * SIZE +
                (dimensions.width + 1) * MARGIN -
                20,
            margin: "auto",
            }}
            icon="arrow-up"
            onClick={()=>shiftView("y", 1)}
        />
        <div style={{ display: "flex" }}>
            <Button
                className="bp3-button"
                style={{
                height:
                    dimensions.height * SIZE +
                    (dimensions.height + 1) * MARGIN -
                    20,
                margin: "10px 0",
                }}
                icon="arrow-left"
                onClick={()=>shiftView("x", -1)}
            />
            <div
                className="map-container"
                >

        </div>
        <Button
            className="bp3-button"
            style={{
              height:
                dimensions.height * SIZE +
                (dimensions.height + 1) * MARGIN -
                20,
              margin: "10px 0",
            }}
            icon="arrow-right"
            onClick={()=>shiftView("x", 1)}
          />
        </div>
        <Button
          className="bp3-button"
          style={{
            width:
              dimensions.width * SIZE +
              (dimensions.width + 1) * MARGIN -
              20,
            margin: "auto",
          }}
          icon="arrow-down"
          onClick={()=>shiftView("y", -1)}
        />
      </div>
    )
}

export default WorldBuilderMap2;