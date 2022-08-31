/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
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
//ON USE
interface UseObject {
    name_prefix: String;
    is_wearable: Boolean;
    name: String;
    desc: String;
}

// EVENTS
interface EventParam {

}

interface Event {
    type: String;
    params: any;
}

//CONSTRAINTS
interface ConstraintParam {

}

interface Constraint {
    type: String;
    params: any;
}

interface OnUseInteraction {
    remaining_uses: Number | null;
    events: Array<Event>
    constraints: Array<Constraint>
}

//WorldObject- Actual Object Node
interface WorldObject {
    agent: Boolean;
    classes: Array<String>;
    contain_size: Number;
    contained_nodes: ContainerNodes;
    container: Boolean;
    container_node: ContainerNodes;
    db_id: String | null;
    dead: Boolean;
    desc: String;
    drink: Boolean;
    equipped: String | null;
    extra_desc: String;
    name: String;
    name_prefix: String;
    names: Array<String>;
    node_id: String;
    object: Boolean;
    on_use: OnUseInteraction;
    plural: String|null;
  }
  
/* STATE TYPE */
interface WorldObjectsState {
  worldObjects: Array<WorldObject>;
  selectedObject: WorldObject | null;
}

/* Initial value of the state */
const initialState: WorldObjectsState = {
    worldObjects: [],
    selectedObject: null
};

//Create slice will generate action objects for us
const worldObjectsSlice = createSlice({
  name: "worldObjects",
  initialState,
  /* REDUCER ACTIONS */
  reducers: {
        updateObjects(state, action: PayloadAction<Array<WorldObject>>){
            return {
                ...state,
                worldObjects: action.payload
            }
        },
        selectObject(state, action: PayloadAction<WorldObject>) {
            return {
                ...state,
                selectedObject: action.payload,
            };
        },
        updateSelectedObject(state, action: PayloadAction<WorldObject>) {
            return {
                ...state,
                selectedObject: action.payload,
            };
        },
        addObject(state, action: PayloadAction<WorldObject>) {
            return {
                ...state,
                worldObjects: [...state.worldObjects, action.payload],
            };
        },
        removeObject(state, action: PayloadAction<string>) {
            const updatedObjects = state.worldObjects.filter(object=>(object.node_id!==action.payload))
            return {
                ...state,
                worldObjects: updatedObjects,
            };
        },
    }
});

/* EXPORTED REDUCER ACTIONS */
// import anywhere in app to use
export const {
    updateObjects,
    selectObject,
    updateSelectedObject,
    addObject,
    removeObject
} = worldObjectsSlice.actions;
/* SLICE REDUCER */
export default worldObjectsSlice.reducer;