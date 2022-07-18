/* REDUX */
import { createSlice, PayloadAction } from "@reduxjs/toolkit";

/* STATE TYPE */
interface ErrorsState {
    showError: Boolean;
    errorMessage: String;
}

/* Initial value of the state */
const initialState: ErrorsState = {
    showError: false,
    errorMessage: "There was an Error"
};

//Create slice will generate action objects for us
const errorsSlice = createSlice({
    name: "errors",
    initialState,
    /* REDUCER ACTIONS */
    reducers: {
        setShowError(state, action: PayloadAction<boolean>) {
            state.showError= action.payload
        },
        setErrorMessage(state, action: PayloadAction<string>) {
            state.errorMessage= action.payload
        }
    }
});

/* EXPORTED REDUCER ACTIONS */
// import anywhere in app to use
export const {
    setShowError,
    setErrorMessage
} = errorsSlice.actions;
/* SLICE REDUCER */
export default errorsSlice.reducer;
