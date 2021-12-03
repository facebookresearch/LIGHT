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
    worldBorders,
    tileClickFunction,
    floor
  })=> {
    //REACT ROUTER

    /* REDUX DISPATCH FUNCTION */
    const dispatch = useAppDispatch();
    /* ------ REDUX STATE ------ */

    /* ------ LOCAL STATE ------ */
    const [viewLoc, setViewLoc] = useState(
        {
            x: -20,
            y: -20
        }
    )
    const [gridData, setGridData] = useState(null)

    /* REACT LIFECYCLE */
    useEffect(()=>{
        let updatedGridData = gridDataGenerator(worldBorders, worldRoomsData, floor);
        console.log("GRID DATA OBJECT  ", updatedGridData)
        setGridData(updatedGridData)
    },[worldRoomsData, floor])
    /* ------ Handlers ------ */
    const shiftView = (axes, amount)=>{
      let updatedView = viewLoc
        axes.map((axis, index)=>{
          updatedView = {...updatedView, [axis]: updatedView[axis]+amount[index]}
        })
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
        <div>
          <Button
              className="bp3-button"
              style={{
                width: "20px",
                height: "20px",
              }}
              icon="arrow-top-left"
              onClick={()=>shiftView(["x","y"], [40, 40])}
          />
          <Button
              className="bp3-button"
              style={{
                width: "1000px",
                height: "20px",
              }}
              icon="arrow-up"
              onClick={()=>shiftView(["y"], [40])}
          />
          <Button
              className="bp3-button"
              style={{
                width: "20px",
                height: "20px",
              }}
              icon="arrow-top-right"
              onClick={()=>shiftView(["x","y"], [-40, 40])}
          />
        </div>
        <div style={{ display: "flex" }}>
            {
              viewLoc.x<=0
              ?
              <Button
                className="bp3-button"
                style={{
                height: "800px",
                width:"20px"
                }}
                icon="arrow-left"
                onClick={()=>shiftView(["x"], [40])}
            />:
            <div                 
              style={{
                height: "800px",
                width:"20px"
              }}
            />
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
                            tileClickFunction={tileClickFunction}
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
            onClick={()=>shiftView(["x"], [-40])}
          />
        </div>
        <div>
          <Button
              className="bp3-button"
              style={{
                width: "20px",
                height: "20px",
              }}
              icon="arrow-bottom-left"
              onClick={()=>shiftView(["x", "y"], [40, -40])}
          />
          <Button
            className="bp3-button"
            style={{
              width:"1000px",
            }}
            icon="arrow-down"
            onClick={()=>shiftView(["y"], [-40])}
          />
          <Button
            className="bp3-button"
            style={{
              width: "20px",
              height: "20px",
            }}
            icon="arrow-bottom-right"
            onClick={()=>shiftView(["x", "y"], [-40, -40])}
          />
        </div>
      </div>
    )
}

export default WorldBuilderMap2;