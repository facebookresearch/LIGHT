//REDUX
import { createSlice, PayloadAction } from "@reduxjs/toolkit";

/* TYPING THE STATE */
interface XpState {
  value: number;
}

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

export const { updateXp } = xpSlice.actions;
export default xpSlice.reducer;
