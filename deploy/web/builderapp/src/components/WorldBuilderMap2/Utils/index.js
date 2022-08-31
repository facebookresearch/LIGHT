
/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

//REACT
import React from "react";

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
    const {top, bottom, left, right} = gridBorders;
    let gridData = {};
    let floors = [];
    for(let k = currentFloor-1; k <= currentFloor+1; k++){
        let floorData = {}
        let rows =[];
        for(let i = top+1; i >= bottom-1; i-- ){
            let row = [];
            for(let j = left-1; j <= right+1; j++){
                let tileData = {
                    agent: false,
                    brightness: null,
                    classes: ["room"],
                    contain_size: 0,
                    contained_nodes: {},
                    db_id: null,
                    is_indoors:null,
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
                    temperature: null
                };
                let coordinateKey = `${j}, ${i}, ${k}`;
                worldRoomsData.map((roomData)=>{
                    if(roomChecker(j, i, k, roomData)){
                        tileData=roomData;
                    }
                })
                //floorData[coordinateKey]=tileData
                row.push(tileData)
            }
            rows.push(row);
        }

        floors.push(rows);
    }
    gridData.floors = floors;
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
