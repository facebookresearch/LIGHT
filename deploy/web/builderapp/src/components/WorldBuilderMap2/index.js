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
import "./styles.css"
/* UTILS */
import {calculateMapBorders, gridDataGenerator} from "./Utils"

const WorldBuilderMap2 = ({
    worldRoomsData, 
    worldBorders
  })=> {
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
    const [viewLoc, setViewLoc] = useState(
        {
            x: -20,
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
          width: "100%",
          textAlign: "center",
          display:"flex",
          justifyContent:"center",
          alignItems:"center",
          flexDirection:"column"
        }}
    >
        <Button
            className="bp3-button"
            style={{
              width: "1000px"
            }}
            icon="arrow-up"
            onClick={()=>shiftView("y", 40)}
        />
        <div style={{ display: "flex" }}>
            {
              viewLoc.x<-20
              ?
              <Button
                className="bp3-button"
                style={{
                height: "800px",
                }}
                icon="arrow-left"
                onClick={()=>shiftView("x", 40)}
            />:
            <div/>
            }
            <div
                className="map-container"
                >
                    {
                        gridData
                        ?
                        <Grid
                            gridData={gridData}
                            borders={worldBorders}
                            xOffset={viewLoc.x}
                            yOffset={viewLoc.y}
                        />
                        :
                        null // NOTE: Add loading icon and placeholder div in future
                    } 
            </div>
        <Button
            className="bp3-button"
            style={{
              height:"800px"
            }}
            icon="arrow-right"
            onClick={()=>shiftView("x", -40)}
          />
        </div>
        <Button
          className="bp3-button"
          style={{
            width:"1000px",
          }}
          icon="arrow-down"
          onClick={()=>shiftView("y", -40)}
        />
      </div>
    )
}

export default WorldBuilderMap2;