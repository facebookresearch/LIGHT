/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

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
import { gridDataGenerator} from "./Utils"

const WorldBuilderMap2 = ({
    worldRoomsData,
    worldBorders,
    tileClickFunction,
    floor,
    width,
    height,
    addRoom,
    updateRoom,
    connectRooms,
    disconnectRooms
  })=> {
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
        if(worldRoomsData && worldBorders){
          console.log("WORLD ROOMS DATA PRE PROCESSED:  ", worldRoomsData)
          let updatedGridData = gridDataGenerator(worldBorders, worldRoomsData, floor);
          console.log("GRID DATA PROCESSED:  ", updatedGridData)
          setGridData(updatedGridData)
        }
    },[ worldRoomsData, worldBorders, floor])

    useEffect(()=>{
      let initialViewLoc = {
        x: width/2,
        y: height/2
      }
      setViewLoc(initialViewLoc)
    },[width, height])

    /* ------ Handlers ------ */
    const shiftView = (axes, amount)=>{
      let updatedView = viewLoc;
        axes.map((axis, index)=>{
          updatedView = {...updatedView, [axis]: updatedView[axis]+amount[index]}
        })
        setViewLoc(updatedView)
    }
    // const mapUpdateHandler = (id, update)=>{
    //   let updatedWorldData = mapWorldData.map((room, index)=>{
    //     let updatedRoom = room;
    //     if(id===room.node_id){
    //       updatedRoom = update;
    //     }
    //     return updatedRoom
    //   })

    //   setMapWorldData(updatedWorldData)
    // }
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
                            borders={worldBorders}
                            xOffset={viewLoc.x}
                            yOffset={viewLoc.y}
                            tileClickFunction={tileClickFunction}
                            connectRooms={connectRooms}
                            disconnectRooms={disconnectRooms}
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
