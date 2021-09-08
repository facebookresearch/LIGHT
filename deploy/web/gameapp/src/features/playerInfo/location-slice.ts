//REDUX
import { createSlice, PayloadAction } from "@reduxjs/toolkit";

/* TYPING THE STATE */
interface LocationState {
  description: string;
  id: string;
  name: string;
}

const initialState: LocationState = {
  description: "",
  id: "",
  name: "",
};
//Create slice will generate action objects for us
const locationSlice = createSlice({
  name: "location",
  initialState,
  /* REDUCER ACTIONS */
  reducers: {
    //immer will handle immutability in state changess
    updateLocation(state, action: PayloadAction<LocationState>) {
      return { ...state, ...action.payload };
    },
  },
});

export const { updateLocation } = locationSlice.actions;
export default locationSlice.reducer;
