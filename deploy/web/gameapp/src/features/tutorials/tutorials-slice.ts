/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REDUX */
import { createSlice, PayloadAction } from "@reduxjs/toolkit";

/* STATE TYPE */
interface TutorialState {
  inHelpMode: boolean;
  selectedTip: number;
}

/* Initial value of the state */
const initialState: TutorialState = {
  inHelpMode: false,
  selectedTip: 0,
};
//Create slice will generate action objects for us
const tutorialSlice = createSlice({
  name: "tutorial",
  initialState,
  /* REDUCER ACTIONS */
  reducers: {
    updateInHelpMode(state, action: PayloadAction<boolean>) {
      return { ...state, inHelpMode: action.payload };
    },
    updateSelectedTip(state, action: PayloadAction<number>) {
      return { ...state, selectedTip: action.payload };
    },
  },
});

/* EXPORTED REDUCER ACTIONS */
// import anywhere in app to use
export const { updateInHelpMode, updateSelectedTip } = tutorialSlice.actions;
/* SLICE REDUCER */
export default tutorialSlice.reducer;
