/* REDUX */
import { createSlice, PayloadAction } from "@reduxjs/toolkit";

/* STATE TYPE */
interface SessionSpentGiftXpState {
  value: number;
}

/* Initial value of the state */
const initialState: SessionSpentGiftXpState = {
  value: 0,
};
//Create slice will generate action objects for us
const sessionSpentGiftXpSlice = createSlice({
  name: "sessionSpentGiftXp",
  initialState,
  /* REDUCER ACTIONS */
  reducers: {
    updateSessionSpentGiftXp(
      state,
      action: PayloadAction<SessionSpentGiftXpState>
    ) {
      return { ...state, ...action.payload };
    },
  },
});

/* EXPORTED REDUCER ACTIONS */
// import anywhere in app to use
export const { updateSessionSpentGiftXp } = sessionSpentGiftXpSlice.actions;
/* SLICE REDUCER */
export default sessionSpentGiftXpSlice.reducer;
