/* REDUX */
import { createSlice, PayloadAction } from "@reduxjs/toolkit";

/* STATE TYPE */
interface ChatInputState {
  text: string;
}

/* Initial value of the state */
const initialState: ChatInputState = {
  text: "",
};

//Create slice will generate action objects for us
const chatInputSlice = createSlice({
  name: "chatInput",
  initialState,
  /* REDUCER ACTIONS */
  reducers: {
    updateChatText(state, action: PayloadAction<string>) {
      return { ...state, text: action.payload };
    },
  },
});

/* EXPORTED REDUCER ACTIONS */
// import anywhere in app to use
export const { updateChatText } = chatInputSlice.actions;
/* SLICE REDUCER */
export default chatInputSlice.reducer;
