//REDUX
import { createSlice, PayloadAction } from "@reduxjs/toolkit";

/* STATE TYPE */
interface LocationState {
  description: string;
  id: string;
  name: string;
}

/* Initial value of the state */
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
    updateLocation(state, action: PayloadAction<LocationState>) {
      return { ...state, ...action.payload };
    },
  },
});

/* EXPORTED REDUCER ACTIONS */
// import anywhere in app to use
export const { updateLocation } = locationSlice.actions;
/* SLICE REDUCER */
export default locationSlice.reducer;
