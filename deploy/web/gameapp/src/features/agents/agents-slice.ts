/* REDUX */
import { createSlice, PayloadAction } from "@reduxjs/toolkit";

/* STATE TYPE */
interface AgentsState {
  [key: string]: string;
}

/* Initial value of the state */
const initialState: AgentsState = {};

//Create slice will generate action objects for us
const agentsSlice = createSlice({
  name: "agents",
  initialState,
  /* REDUCER ACTIONS */
  reducers: {
    updateAgents(state, action: PayloadAction<AgentsState>) {
      return { ...state, ...action.payload };
    },
  },
});

/* EXPORTED REDUCER ACTIONS */
// import anywhere in app to use
export const { updateAgents } = agentsSlice.actions;
/* SLICE REDUCER */
export default agentsSlice.reducer;
