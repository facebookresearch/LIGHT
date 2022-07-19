/* REDUX */
import { createSlice, PayloadAction } from "@reduxjs/toolkit";

/* STATE TYPE */
interface LoadingState {
    showLoadingSpinner: Boolean;
}

/* Initial value of the state */
const initialState: LoadingState = {
    showLoadingSpinner: false,
};

//Create slice will generate action objects for us
const loadingSlice = createSlice({
    name: "loading",
    initialState,
    /* REDUCER ACTIONS */
    reducers: {
        setIsLoading(state, action: PayloadAction<boolean>) {
            state.showLoadingSpinner= action.payload
        }
    }
});

/* EXPORTED REDUCER ACTIONS */
// import anywhere in app to use
export const {
    setIsLoading,
} = loadingSlice.actions;
/* SLICE REDUCER */
export default loadingSlice.reducer;
