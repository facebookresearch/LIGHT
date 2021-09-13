/* REDUX */
import { createSlice, PayloadAction } from "@reduxjs/toolkit";

/* STATE TYPE */
interface TutorialState {
  inHelpMode: boolean;
  tutorialTips: Array<number>;
  selectedTip: number;
}

/* Initial value of the state */
const initialState: TutorialState = {
  inHelpMode: false,
  tutorialTips: [],
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
