/* REDUX */
import { createSlice, PayloadAction } from "@reduxjs/toolkit";

/* STATE TYPE */
interface EmojiState {
  selectedEmoji: string;
}

/* Initial value of the state */
const initialState: EmojiState = {
  selectedEmoji: "?",
};

//Create slice will generate action objects for us
const emojiSlice = createSlice({
  name: "emoji",
  initialState,
  /* REDUCER ACTIONS */
  reducers: {
    updateEmoji(state, action: PayloadAction<string>) {
      state.selectedEmoji = action.payload;
    },
  },
});

/* EXPORTED REDUCER ACTIONS */
// import anywhere in app to use
export const { updateEmoji } = emojiSlice.actions;
/* SLICE REDUCER */
export default emojiSlice.reducer;
