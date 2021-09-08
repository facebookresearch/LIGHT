//REDUX
import { createSlice, PayloadAction } from "@reduxjs/toolkit";

/* TYPING THE STATE */
interface GiftXpState {
  value: number;
}

const initialState: GiftXpState = {
  value: 0,
};
//Create slice will generate action objects for us
const giftXpSlice = createSlice({
  name: "giftXp",
  initialState,
  /* REDUCER ACTIONS */
  reducers: {
    //immer will handle immutability in state changess
    updateGiftXp(state, action: PayloadAction<GiftXpState>) {
      return { ...state, ...action.payload };
    },
    decrementGiftXp(state) {
      state.value--;
    },
  },
});

export const { updateGiftXp } = giftXpSlice.actions;
export default giftXpSlice.reducer;
