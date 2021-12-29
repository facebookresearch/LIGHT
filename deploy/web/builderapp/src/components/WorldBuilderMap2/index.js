/* REACT */
import React, {useEffect, useState} from 'react';

/* REDUX */

/* CUSTOM COMPONENTS */
import Grid from "./Grid"
/* BLUEPRINT JS COMPONENTS */
import {Button } from "@blueprintjs/core";
/* STYLES */
import "./styles.css"
/* UTILS */
import {calculateMapBorders, gridDataGenerator} from "./Utils"

const WorldBuilderMap2 = ({
    worldRoomsData, 
    worldBorders,
    tileClickFunction,
    floor,
    width,
    height
  })=> {
    //REACT ROUTER

    /* ------ LOCAL STATE ------ */
    const [mapWorldData, setMapWorldData] = useState(null)
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
    },[ worldRoomsData, worldBorders, floor])

    useEffect(()=>{
      let initialViewLoc = {
        x: width/4,
        y: height/4
      }
      console.log("INITIAL VIEW LOC", initialViewLoc)
      setViewLoc(initialViewLoc)
    },[gridData])

    /* ------ Handlers ------ */
    const shiftView = (axes, amount)=>{
      let updatedView = viewLoc;
        axes.map((axis, index)=>{
          updatedView = {...updatedView, [axis]: updatedView[axis]+amount[index]}
        })
        console.log("UPDATED VIEW", updatedView)
        setViewLoc(updatedView)
    }
    const HandleMapUpdate = (id, update)=>{
      let updatedGridData = gridData.map((room, index)=>{
        let updatedRoom = room;
        if(id===room.node_id){
          updatedRoom = update;
        }
        return updatedRoom
      })
      setGridData(updatedGridData)
    }
    return(
    <div className="map-container">
        <div className="button-row ">
          {
           ( viewLoc.x<=0 && viewLoc.y<=0)
            ?
          <Button
              className="bp3-button"
              style={{
                width: "20px",
                height: "20px",
              }}
              icon="arrow-top-left"
              onClick={()=>shiftView(["x","y"], [40, 40])}
          />
          :
          <div                 
            style={{
              height: "20px",
              width:"20px"
            }}
          />
            
          }
          {
            viewLoc.y<=0
            ?
            <Button
                className="bp3-button"
                style={{
                  width: "1000px",
                  height: "20px",
                }}
                icon="arrow-up"
                onClick={()=>shiftView(["y"], [40])}
            />
            :
            <div                 
            style={{
              height: "20px",
              width:"1000px"
            }}
          />
          }
          {
          ((viewLoc.x > (width+200)) && (viewLoc.y<=0))
          ?
          <Button
              className="bp3-button"
              style={{
                width: "20px",
                height: "20px",
              }}
              icon="arrow-top-right"
              onClick={()=>shiftView(["x","y"], [-40, 40])}
          />
          :
          <div                 
          style={{
            height: "20px",
            width:"20px"
          }}
        />
          }
        </div>
        <div className="view-row">
            {
              viewLoc.x<=0
              ?
              <Button
                className="button"
                style={{
                height: "800px",
                width:"20px"
                }}
                icon="arrow-left"
                onClick={()=>shiftView(["x"], [40])}
            />
            :
            <div                 
              style={{
                height: "800px",
                width:"20px"
              }}
            />
            }
            <div
                className="view-container"
                >
                    {
                        gridData
                        ?
                        <Grid
                            gridData={gridData}
                            gridUpdateFunction = {HandleMapUpdate}
                            borders={worldBorders}
                            xOffset={viewLoc.x}
                            yOffset={viewLoc.y}
                            tileClickFunction={tileClickFunction}
                        />
                        :
                        null // NOTE: Add loading icon and placeholder div in future
                    } 
            </div>
        {
          (viewLoc.x > width+250)
          ?
          <Button
              className="bp3-button"
              style={{
                height:"800px"
              }}
              icon="arrow-right"
              onClick={()=>shiftView(["x"], [-40])}
            />
            :
            <div                 
            style={{
              height: "800px",
              width:"20px"
            }}
          />
        }
        </div>
        <div className="button-row">
        {
            (viewLoc.y>=height+200 && viewLoc.x<=0 )
            ?
          <Button
              className="bp3-button"
              style={{
                width: "20px",
                height: "20px",
              }}
              icon="arrow-bottom-left"
              onClick={()=>shiftView(["x", "y"], [40, -40])}
          />
          :
          <div                 
            style={{
              height: "20px",
              width:"20px"
            }}
          />
          }
          {
            (viewLoc.y >= height+200)
              ?
            <Button
              className="bp3-button"
              style={{
                width:"1000px",
              }}
              icon="arrow-down"
              onClick={()=>shiftView(["y"], [-40])}
            />
            :
            <div                 
              style={{
                height: "20px",
                width:"1000px"
              }}
            />
          }
          {
            (viewLoc.y>=height+200 && viewLoc.x > width+250)
            ?
            <Button
              className="bp3-button"
              style={{
                width: "20px",
                height: "20px",
              }}
              icon="arrow-bottom-right"
              onClick={()=>shiftView(["x", "y"], [-40, -40])}
            />
            :
            <div                 
              style={{
                height: "20px",
                width:"20px"
              }}
            />
          }
        </div>
      </div>
    )
}

export default WorldBuilderMap2;