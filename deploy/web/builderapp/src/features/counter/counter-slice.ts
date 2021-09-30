//REDUX
import {createSlice, PayloadAction} from "@reduxjs/toolkit"

/* TYPING THE STATE */
interface CounterState {
    value: number;
}

/* Initial value of the state */
const initialState: CounterState = {
    value:0
}
//Create slice will generate action objects for us

const counterSlice = createSlice({
    name:'counter',
    initialState,
    /* REDUCER ACTIONS */
    reducers: {
        incremented(state){ //immer, a library running under the hood, will handle immutability in state changes
            state.value++;
        },
        amountAdded(state, action:PayloadAction<number>) {
            state.value += action.payload;
        }
    }
})

/* EXPORTED REDUCER ACTIONS */
//import anywhere in app to use
export const { incremented, amountAdded } = counterSlice.actions;
/* SLICE REDUCER */
export default counterSlice.reducer;