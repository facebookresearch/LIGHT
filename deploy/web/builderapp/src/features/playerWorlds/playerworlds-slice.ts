/* REDUX */
import { createSlice, PayloadAction } from "@reduxjs/toolkit";
/* CUSTOM TYPES */
interface World {
    id: Number;
    name:String;
  }
  
/* STATE TYPE */
interface PlayerWorldsState {
  customWorlds: Array<string>;
  selectedWorld: World | null;
}

/* Initial value of the state */
const initialState: PlayerWorldsState = {
    customWorlds: [],
    selectedWorld: null
};

//Create slice will generate action objects for us
const playerWorldsSlice = createSlice({
  name: "playerWorlds",
  initialState,
  /* REDUCER ACTIONS */
  reducers: {
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
        updatePlayerWorlds(state, action: PayloadAction<string>) {
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
    selectWorld,
    updatePlayerWorlds
} = playerWorldsSlice.actions;
/* SLICE REDUCER */
export default playerWorldsSlice.reducer;