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
interface PlayerWorldState {
  worldDraft: World | null;
  selectedWorld: World | null;
}

/* Initial value of the state */
const initialState: PlayerWorldState = {
    worldDraft: null,
    selectedWorld: null
};

//Create slice will generate action objects for us
const playerWorldSlice = createSlice({
  name: "playerWorld",
  initialState,
  reducers: {
        setWorldDraft(state, action: PayloadAction<World>){
            return {
                ...state,
                worldDraft: action.payload
            }
        },
        updateSelectedWorld(state, action: PayloadAction<World>) {
            return {
                ...state,
                selectedWorld: action.payload,
            };
        }
    }
});

/* EXPORTED REDUCER ACTIONS */
// import anywhere in app to use
export const {
    setWorldDraft,
    updateSelectedWorld,
} = playerWorldSlice.actions;
/* SLICE REDUCER */
export default playerWorldSlice.reducer;
