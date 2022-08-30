
/*****
 * Copyright (c) Meta Platforms, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REDUX */
import { createSlice, PayloadAction } from "@reduxjs/toolkit";
/* CUSTOM TYPES */
//Container
interface ContainerNode {
    target_id: String;
}

interface ContainerNodes {
    [key: string]: ContainerNode;
}
//Neighbor
interface Neighbor {
    examine_desc: string;
    label: string;
    locked_edge: any;
    target_id: string;
}

interface Neighbors {
    [key: string]: Neighbor;
}

//Room-Actual Node in Array of rooms
interface Room {
    agent: Boolean;
    classes: Array<string>;
    contain_size: Number;
    contained_nodes: ContainerNodes;
    db_id: string | null;
    is_indoors: boolean | null;
    desc: string;
    extra_desc: string;
    name: string;
    name_prefix: string;
    names: Array<string>;
    neighbors: Neighbors;
    node_id: string;
    object:boolean;
    room:boolean;
    size:number;
    grid_location: Array<Number>;
    surface_type: string;
    color: string | null;
    brightness: number | null;
    temperature: number | null;
  }
  
/* STATE TYPE */
interface WorldRoomsState {
  worldRooms: Array<Room>;
  selectedRoom: Room | null;
}

/* Initial value of the state */

const initialState: WorldRoomsState = {
    worldRooms: [],
    selectedRoom: null
};

//Create slice will generate action objects for us
const worldRoomsSlice = createSlice({
  name: "worldRooms",
  initialState,
  /* REDUCER ACTIONS */
  reducers: {
        updateRooms(state, action: PayloadAction<Array<Room>>){
            return {
                ...state,
                worldRooms: action.payload
            }
        },
        selectRoom(state, action: PayloadAction<Room>) {
            return {
                ...state,
                selectedRoom: action.payload,
            };
        },
        updateSelectedRoom(state, action: PayloadAction<Room>) {
            return {
                ...state,
                selectedRoom: action.payload,
            };
        },
        addRoom(state, action: PayloadAction<Room>) {
            return {
                ...state,
                worldRooms: [...state.worldRooms, action.payload],
            };
        },
        removeRoom(state, action: PayloadAction<string>) {
            const updatedRooms = state.worldRooms.filter(room=>(room.node_id!==action.payload))
            return {
                ...state,
                worldRooms: updatedRooms,
            };
        },
    }
});

/* EXPORTED REDUCER ACTIONS */
// import anywhere in app to use
export const {
    updateRooms,
    selectRoom,
    updateSelectedRoom,
    addRoom,
    removeRoom
} = worldRoomsSlice.actions;
/* SLICE REDUCER */
export default worldRoomsSlice.reducer;