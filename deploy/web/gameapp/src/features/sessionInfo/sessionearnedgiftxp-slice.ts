/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REDUX */
import { createSlice, PayloadAction } from "@reduxjs/toolkit";

/* STATE TYPE */
interface SessionEarnedGiftXpState {
  value: number;
}

/* Initial value of the state */
const initialState: SessionEarnedGiftXpState = {
  value: 0,
};
//Create slice will generate action objects for us
const sessionEarnedGiftXpSlice = createSlice({
  name: "sessionEarnedGiftXp",
  initialState,
  /* REDUCER ACTIONS */
  reducers: {
    updateSessionEarnedGiftXp(state, action: PayloadAction<number>) {
      return { ...state, value: action.payload };
    },
  },
});

/* EXPORTED REDUCER ACTIONS */
// import anywhere in app to use
export const { updateSessionEarnedGiftXp } = sessionEarnedGiftXpSlice.actions;
/* SLICE REDUCER */
export default sessionEarnedGiftXpSlice.reducer;
