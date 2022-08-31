/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REDUX */
import { createSlice, PayloadAction } from "@reduxjs/toolkit";
/* CUSTOM TYPES */



interface World {
    id: Number;
    agents: Array<string>;
    nodes: any;
    name:String;
    objects: Array<string>;
    room: Array<string>;
  }
  
/* STATE TYPE */
interface PlayerWorldsState {
  customWorlds: Array<World>;
  worldDrafts: Array<World>;
  selectedWorld: World | null;
}

/* Initial value of the state */
const initialState: PlayerWorldsState = {
    customWorlds: [],
    worldDrafts:[],
    selectedWorld: null
};

//Create slice will generate action objects for us
const playerWorldsSlice = createSlice({
  name: "playerWorlds",
  initialState,
  /* REDUCER ACTIONS */
  reducers: {
        fetchWorlds(state, action: PayloadAction<Array<World>>){
            return {
                ...state,
                customWorlds: action.payload
            }
        },
        setWorldDrafts(state, action: PayloadAction<Array<World>>){
            return {
                ...state,
                worldDrafts: action.payload
            }
        },
        selectWorld(state, action: PayloadAction<World>) {
            return {
                ...state,
                selectedWorld: action.payload,
            };
        },
        updateSelectedWorld(state, action: PayloadAction<World>) {
            return {
                ...state,
                selectedWorld: action.payload,
            };
        },
        updatePlayerWorlds(state, action: PayloadAction<World>) {
            return {
                ...state,
                customWorlds: [...state.customWorlds, action.payload],
            };
        },
    }
});

/* EXPORTED REDUCER ACTIONS */
// import anywhere in app to use
export const {
    fetchWorlds,
    setWorldDrafts,
    selectWorld,
    updateSelectedWorld,
    updatePlayerWorlds
} = playerWorldsSlice.actions;
/* SLICE REDUCER */
export default playerWorldsSlice.reducer;