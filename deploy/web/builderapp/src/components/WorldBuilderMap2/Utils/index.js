import React from "react";
import { Colors } from "@blueprintjs/core";
import { cloneDeep, isEmpty, merge } from "lodash";
import equal from "fast-deep-equal";
import { emojiIndex } from "emoji-mart";

//Generates data for grid
export function gridDataGenerator(gridBorders, roomData, currentFloor){
    const {top, bottom, left, right} = gridBorders;
    let gridData = {};
    let tileData = {

    };
    for( ){
        for(){

        }
    }
}
// Sets "edges" of world map using the most extreme x and y values on the matrix 
export function calculateMapBorders(roomNodes){
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
        borders.bottom = borders.top < y ? borders.top : y;
        borders.right = borders.right > x ? borders.top : x;
        borders.left = borders.left < x ? borders.left : x;
    })
    return borders;
}
