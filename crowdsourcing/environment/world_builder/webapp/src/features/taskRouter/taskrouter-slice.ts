/* REDUX */
import { createSlice, PayloadAction } from "@reduxjs/toolkit";

/* STATE TYPE */
interface TaskRouterState {
    currentLocation: String;
    builderRouterHistory: Array<String>;

}

/* Initial value of the state */
const initialState: TaskRouterState = {
    currentLocation: "/",
    builderRouterHistory: [],
};

//Create slice will generate action objects for us
const taskRouterSlice = createSlice({
    name: "taskRouter",
    initialState,
    /* REDUCER ACTIONS */
    reducers: {
        setTaskRouterCurrentLocation(state, action: PayloadAction<string>) {
            state.currentLocation= action.payload
        },
        updTaskRouterHistory(state, action: PayloadAction<Array<String>>) {
            state.builderRouterHistory= action.payload
        },
    }
});

/* EXPORTED REDUCER ACTIONS */
// import anywhere in app to use
export const {
    setTaskRouterCurrentLocation,
    updTaskRouterHistory
} = taskRouterSlice.actions;
/* SLICE REDUCER */
export default taskRouterSlice.reducer;
