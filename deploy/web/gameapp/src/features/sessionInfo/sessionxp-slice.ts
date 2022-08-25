/* REDUX */
import { createSlice, PayloadAction } from "@reduxjs/toolkit";

/* STATE TYPE */
interface SessionXpState {
  value: number;
}

/* Initial value of the state */
const initialState: SessionXpState = {
  value: 0,
};
//Create slice will generate action objects for us
const sessionXpSlice = createSlice({
  name: "sessionXp",
  initialState,
  /* REDUCER ACTIONS */
  reducers: {
    updateSessionXp(state, action: PayloadAction<number>) {
      return { ...state, value: action.payload };
    },
  },
});

/* EXPORTED REDUCER ACTIONS */
// import anywhere in app to use
export const { updateSessionXp } = sessionXpSlice.actions;
/* SLICE REDUCER */
export default sessionXpSlice.reducer;
