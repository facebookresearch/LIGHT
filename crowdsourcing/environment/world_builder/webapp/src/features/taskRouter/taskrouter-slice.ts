/* REDUX */
import { createSlice, PayloadAction } from "@reduxjs/toolkit";

/* STATE TYPE */
interface TaskRouterState {
    currentLocation: String;
    taskRouterHistory: Array<String>;

}

/* Initial value of the state */
const initialState: TaskRouterState = {
    currentLocation: "/",
    taskRouterHistory: [],
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
            state.taskRouterHistory= action.payload
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
