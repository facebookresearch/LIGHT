/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

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
    updateSessionSpentGiftXp(state, action: PayloadAction<number>) {
      return { ...state, value: action.payload };
    },
  },
});

/* EXPORTED REDUCER ACTIONS */
// import anywhere in app to use
export const { updateSessionSpentGiftXp } = sessionSpentGiftXpSlice.actions;
/* SLICE REDUCER */
export default sessionSpentGiftXpSlice.reducer;
