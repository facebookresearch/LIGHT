//REDUX
import { createSlice, PayloadAction } from "@reduxjs/toolkit";

/* STATE TYPE */
interface MessagesState {
  value: number;
}

/* Initial value of the state */
const initialState: MessagesState = {
  value: 0,
};
//Create slice will generate action objects for us
const messagesSlice = createSlice({
  name: "messagesSlice",
  initialState,
  /* REDUCER ACTIONS */
  reducers: {
    updateMessages(state, action: PayloadAction<MessagesState>) {
      return { ...state, ...action.payload };
    },
  },
});

/* EXPORTED REDUCER ACTIONS */
// import anywhere in app to use
export const { updateMessages } = messagesSlice.actions;
/* SLICE REDUCER */
export default messagesSlice.reducer;
