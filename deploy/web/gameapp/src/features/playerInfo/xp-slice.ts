//REDUX
import { createSlice, PayloadAction } from "@reduxjs/toolkit";

/* TYPING THE STATE */
interface XpState {
  description: string;
  id: string;
  name: string;
}

const initialState: XpState = {
  description: "",
  id: "",
  name: "",
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
  },
});

export const { updateXp } = xpSlice.actions;
export default xpSlice.reducer;
