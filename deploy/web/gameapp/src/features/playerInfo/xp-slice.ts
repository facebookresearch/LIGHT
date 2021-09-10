//REDUX
import { createSlice, PayloadAction } from "@reduxjs/toolkit";

/* STATE TYPE */
interface XpState {
  value: number;
}

/* Initial value of the state */
const initialState: XpState = {
  value: 0,
};

//Create slice will generate action objects for us
const xpSlice = createSlice({
  name: "xp",
  initialState,
  /* REDUCER ACTIONS */
  reducers: {
    //immer will handle immutability in state changess
    updateXp(state, action: PayloadAction<XpState>) {
      return { ...state, ...action.payload };
    },
    increaseXp(state, action: PayloadAction<number>) {
      state.value += action.payload;
    },
  },
});

/* EXPORTED REDUCER ACTIONS */
// import anywhere in app to use
export const { updateXp } = xpSlice.actions;
/* SLICE REDUCER */
export default xpSlice.reducer;
