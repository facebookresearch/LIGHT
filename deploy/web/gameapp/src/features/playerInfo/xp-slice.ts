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
  level: number;
  xpToNextLevel: number;
  progressPercent: number;
}

/* Initial value of the state */
const initialState: XpState = {
  value: 0,
  level: 1,
  xpToNextLevel: 0,
  progressPercent: 0,
};

//Create slice will generate action objects for us
const xpSlice = createSlice({
  name: "xp",
  initialState,
  /* REDUCER ACTIONS */
  reducers: {
    updateXp(state, action: PayloadAction<number>) {
      // BASE VALUES
      let currentLevel = 1;
      let currentExp = action.payload;
      let expToLevel = currentLevel * 10;
      // Level is calculated by subtracting total exp by required experience for each level
      while (expToLevel <= currentExp) {
        currentLevel++;
        currentExp -= expToLevel;
        expToLevel = currentLevel * 10;
      }
      let remainingXp = currentExp;
      let updatedPercent = Math.floor((remainingXp / expToLevel) * 100);
      let currentXpToNextLevel = expToLevel - remainingXp;
      return {
        ...state,
        value: action.payload,
        level: currentLevel,
        xpToNextLevel: currentXpToNextLevel,
        progressPercent: updatedPercent,
      };
    },
  },
});

/* EXPORTED REDUCER ACTIONS */
// import anywhere in app to use
export const { updateXp } = xpSlice.actions;
/* SLICE REDUCER */
export default xpSlice.reducer;
