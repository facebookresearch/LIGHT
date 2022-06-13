/* REDUX */
import { createSlice, PayloadAction } from "@reduxjs/toolkit";
/* CUSTOM TYPES */
//Location
interface Location {
    name: String;
    id: String | null;
}

/* STATE TYPE */
interface TaskRouterState {
    currentLocation: Location;
    taskRouterHistory: Array<Location>;
}

/* Initial value of the state */
const initialState: TaskRouterState = {
    currentLocation: {
        name: "map",
        id: null
    },
    taskRouterHistory: []
};

//Create slice will generate action objects for us
const taskRouterSlice = createSlice({
    name: "taskRouter",
    initialState,
    /* REDUCER ACTIONS */
    reducers: {
        setTaskRouterCurrentLocation(state, action: PayloadAction<Location>) {
            state.currentLocation= action.payload
        },
        updateTaskRouterHistory(state, action: PayloadAction<Array<Location>>) {
            state.taskRouterHistory= action.payload
        },
    }
});

/* EXPORTED REDUCER ACTIONS */
// import anywhere in app to use
export const {
    setTaskRouterCurrentLocation,
    updateTaskRouterHistory
} = taskRouterSlice.actions;
/* SLICE REDUCER */
export default taskRouterSlice.reducer;
