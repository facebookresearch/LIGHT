/* REDUX */
import { createSlice, PayloadAction } from "@reduxjs/toolkit";

/* STATE TYPE */
interface SidebarsState {
    showLeftSidebar: Boolean;
    showRightSidebar: Boolean;
}

/* Initial value of the state */
const initialState: SidebarsState = {
    showLeftSidebar: true,
    showRightSidebar: false
};

//Create slice will generate action objects for us
const sidebarsSlice = createSlice({
    name: "sidebars",
    initialState,
    /* REDUCER ACTIONS */
    reducers: {
        setLeftSidebar(state, action: PayloadAction<boolean>) {
            state.showLeftSidebar= action.payload
        },
        setRightSidebar(state, action: PayloadAction<boolean>) {
            state.showRightSidebar= action.payload
        },
    }
});

/* EXPORTED REDUCER ACTIONS */
// import anywhere in app to use
export const {
    setLeftSidebar,
    setRightSidebar
} = sidebarsSlice.actions;
/* SLICE REDUCER */
export default sidebarsSlice.reducer;