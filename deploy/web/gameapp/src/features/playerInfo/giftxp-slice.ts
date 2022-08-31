/*****
 * Copyright (c) Meta Platforms, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REDUX */
import { createSlice, PayloadAction } from "@reduxjs/toolkit";

/* STATE TYPE */
interface GiftXpState {
  value: number;
}

/* Initial value of the state */
const initialState: GiftXpState = {
  value: 0,
};
//Create slice will generate action objects for us
const giftXpSlice = createSlice({
  name: "giftXp",
  initialState,
  /* REDUCER ACTIONS */
  reducers: {
    updateGiftXp(state, action: PayloadAction<GiftXpState>) {
      return { ...state, ...action.payload };
    },
    decrementGiftXp(state) {
      state.value--;
    },
  },
});

/* EXPORTED REDUCER ACTIONS */
// import anywhere in app to use
export const { updateGiftXp } = giftXpSlice.actions;
/* SLICE REDUCER */
export default giftXpSlice.reducer;
