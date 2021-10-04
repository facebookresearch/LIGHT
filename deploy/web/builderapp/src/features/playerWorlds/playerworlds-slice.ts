/* REDUX */
import { createSlice, PayloadAction } from "@reduxjs/toolkit";

/* STATE TYPE */
interface PlayerWorldsState {
  customWorlds: Array<string>;
}

/* Initial value of the state */
const initialState: PlayerWorldsState = {
    customWorlds: []
};

//Create slice will generate action objects for us
const playerWorldsSlice = createSlice({
  name: "playerWorlds",
  initialState,
  /* REDUCER ACTIONS */
  reducers: {
    updatePlayerWorlds(state, action: PayloadAction<string>) {
      return {
        ...state,
        customWorlds: [...state.customWorlds, action.payload],
      };
    },
});

/* EXPORTED REDUCER ACTIONS */
// import anywhere in app to use
export const {
    updatePlayerWorlds
} = playerWorldsSlice.actions;
/* SLICE REDUCER */
export default playerWorldsSlice.reducer;