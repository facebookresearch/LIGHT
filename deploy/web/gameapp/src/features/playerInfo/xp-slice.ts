/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REDUX */
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
    updateXp(state, action: PayloadAction<number>) {
      return { ...state, value: action.payload };
    },
    increaseXp(state, action: PayloadAction<number>) {
      state.value += action.payload;
    },
  },
});

/* EXPORTED REDUCER ACTIONS */
// import anywhere in app to use
export const { updateXp, increaseXp } = xpSlice.actions;
/* SLICE REDUCER */
export default xpSlice.reducer;
