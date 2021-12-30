import React from "react";
import { Colors } from "@blueprintjs/core";
import { cloneDeep, isEmpty, merge } from "lodash";
import equal from "fast-deep-equal";
import { emojiIndex } from "emoji-mart";
//Checks to see if coordinate has existing room data
export function roomChecker(x, y, z, room){
    const {grid_location} = room;
    const roomXLoc = grid_location[0];
    const roomYLoc = grid_location[1];
    const roomZLoc = grid_location[2];
    if(x==roomXLoc && y==roomYLoc && z ==roomZLoc){
        return true
    }
    return false
}

//Generates data for grid
export function gridDataGenerator(gridBorders, worldRoomsData, currentFloor){
    console.log("GRID BORDERS", gridBorders)
    const {top, bottom, left, right} = gridBorders;
    let gridData = {};
    let rows =[];

    for(let i = top+1; i >= bottom-1; i-- ){
        let row = [];
        for(let j = left-1; j <= right+1; j++){
            let tileData = {
                agent: false,
                classes: ["room"],
                contain_size: 0,
                contained_nodes: {},
                db_id: null,
                desc: "",
                extra_desc: "",
                name: "",
                name_prefix: "",
                names:[],
                neighbors: [],
                node_id: "",
                object: false,
                room: true,
                size:1,
                grid_location: [j , i, currentFloor],
                surface_type: "",
            };
            let coordinateKey = `${j}, ${i}, ${currentFloor}`;
            worldRoomsData.map((roomData)=>{
                if(roomChecker(j, i, currentFloor, roomData)){
                    tileData=roomData;
                }
            })
            gridData[coordinateKey]=tileData
            row.push(tileData)
        }
        rows.push(row)
        console.log("ROW", i, row)
    }
    gridData.rows = rows;
    return gridData
}
// Sets "edges" of world map using the most extreme x and y values on the matrix 
export function calculateMapBorders(roomNodes){
    let borders = {
        top: 0,
        bottom: 0,
        left: 0,
        right: 0
    }
    roomNodes.map((roomNode)=>{
        let {grid_location} = roomNode;
        let x = grid_location[0]
        let y = grid_location[1]
        borders.top = borders.top > y ? borders.top : y;
        borders.bottom = borders.top < y ? borders.top : y;
        borders.right = borders.right > x ? borders.top : x;
        borders.left = borders.left < x ? borders.left : x;
    })
    return borders;
}
