/* REDUX */
import { createSlice, PayloadAction } from "@reduxjs/toolkit";

/* STATE TYPE */
interface ViewState {
  isMobile: boolean;
  showDrawer: boolean;
}

/* Initial value of the state */
const initialState: ViewState = {
  isMobile: false,
  showDrawer: false,
};
//Create slice will generate action objects for us
const viewSlice = createSlice({
  name: "view",
  initialState,
  /* REDUCER ACTIONS */
  reducers: {
    updateIsMobile(state, action: PayloadAction<boolean>) {
      return { ...state, isMobile: action.payload };
    },
    updateShowDrawer(state, action: PayloadAction<boolean>) {
      return { ...state, showDrawer: action.payload };
    },
  },
});

/* EXPORTED REDUCER ACTIONS */
// import anywhere in app to use
export const { updateIsMobile, updateShowDrawer } = viewSlice.actions;
/* SLICE REDUCER */
export default viewSlice.reducer;
