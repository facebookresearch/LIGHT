import { createSlice, PayloadAction } from "@reduxjs/toolkit";

interface CounterState {
  value: number;
}

const initialState: CounterState = {
  value: 0,
};
//Create slice will generate action objects for us
const counterSlice = createSlice({
  name: "counter",
  initialState,
  reducers: {
    incremented(state) {
      //immer will handle immutability in state changes
      state.value++;
    },
    amountAdded(state, action: PayloadAction<number>) {
      state.value += action.payload;
    },
  },
});

export const { incremented, amountAdded } = counterSlice.actions;
export default counterSlice.reducer;
