/*****
 * Copyright (c) Meta Platforms, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REDUX */
import { createSlice, PayloadAction } from "@reduxjs/toolkit";

/* STATE TYPE */
interface ChatInputState {
  chatText: string;
  tellTarget: string;
  isSaying: boolean;
  submittedMessages: Array<string>;
}

/* Initial value of the state */
const initialState: ChatInputState = {
  chatText: "",
  tellTarget: "",
  isSaying: true,
  submittedMessages: [],
};

//Create slice will generate action objects for us
const chatInputSlice = createSlice({
  name: "chatInput",
  initialState,
  /* REDUCER ACTIONS */
  reducers: {
    updateChatText(state, action: PayloadAction<string>) {
      return { ...state, chatText: action.payload };
    },
    updateTellTarget(state, action: PayloadAction<string>) {
      return { ...state, tellTarget: action.payload };
    },
    updateIsSaying(state, action: PayloadAction<boolean>) {
      return { ...state, isSaying: action.payload };
    },
    updateSubmittedMessages(state, action: PayloadAction<string>) {
      return {
        ...state,
        submittedMessages: [...state.submittedMessages, action.payload],
      };
    },
  },
});

/* EXPORTED REDUCER ACTIONS */
// import anywhere in app to use
export const {
  updateChatText,
  updateTellTarget,
  updateIsSaying,
  updateSubmittedMessages,
} = chatInputSlice.actions;
/* SLICE REDUCER */
export default chatInputSlice.reducer;
