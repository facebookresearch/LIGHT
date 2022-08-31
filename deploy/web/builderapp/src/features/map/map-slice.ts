
/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REDUX */
import { createSlice, PayloadAction } from "@reduxjs/toolkit";

interface Dimensions {
    width: Number;
    height: Number;
}

interface Borders {
    top:Number;
    bottom:Number;
    left:Number;
    right:Number;
}


/* STATE TYPE */
interface MapState {
    mapWidth: Number;
    mapHeight: Number;
    mapBorders: Borders;
    floor: Number;
}

/* Initial value of the state */
const initialState: MapState = {
    mapWidth: 0,
    mapHeight: 0,
    mapBorders: {
            top: 2,
            bottom: -2,
            left: -2,
            right: 2
        },
    floor: 0,
};

//Create slice will generate action objects for us
const mapSlice = createSlice({
    name: "map",
    initialState,
    /* REDUCER ACTIONS */
    reducers: {
        updateFloor(state, action: PayloadAction<Number>) {
            return {
                ...state,
                floor: action.payload
            }
        },
        updateBorders(state, action: PayloadAction<Borders>){
            return {
                ...state,
                mapBorders: action.payload
            }
        },
        updateDimensions(state, action: PayloadAction<Dimensions>){
            const {height, width} = action.payload
            return {
                ...state,
                mapHeight: height,
                mapWidth: width
            }
        },
    }
});

/* EXPORTED REDUCER ACTIONS */
// import anywhere in app to use
export const {
    updateFloor,
    updateBorders,
    updateDimensions,
} = mapSlice.actions;
/* SLICE REDUCER */
export default mapSlice.reducer;