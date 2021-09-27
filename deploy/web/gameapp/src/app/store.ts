/* REDUX */
import { configureStore } from "@reduxjs/toolkit";
//REDUCERS
import agentsReducer from "../features/agents/agents-slice";
import chatInputReducer from "../features/chatInput/chatinput-slice";
import emojiReducer from "../features/playerInfo/emoji-slice";
import giftXpReducer from "../features/playerInfo/giftxp-slice";
import locationReducer from "../features/playerInfo/location-slice";
import messagesReducer from "../features/messages/messages-slice";
import personaReducer from "../features/playerInfo/persona-slice";
import sessionXpReducer from "../features/sessionInfo/sessionxp-slice";
import sessionSpentGiftXpReducer from "../features/sessionInfo/sessionspentgiftxp-slice";
import tutorialsReducer from "../features/tutorials/tutorials-slice";
import viewReducer from "../features/view/view-slice";
import xpReducer from "../features/playerInfo/xp-slice";

//Store - Redux store that as a "bank" of state components can subscribe to
export const store = configureStore({
  //Combined reducer of all slices
  reducer: {
    agents: agentsReducer,
    chatInput: chatInputReducer,
    emoji: emojiReducer,
    giftXp: giftXpReducer,
    location: locationReducer,
    messages: messagesReducer,
    persona: personaReducer,
    sessionXp: sessionXpReducer,
    sessionSpentGiftXp: sessionSpentGiftXpReducer,
    tutorials: tutorialsReducer,
    view: viewReducer,
    xp: xpReducer,
  },
});

// AppDispatch - function that that takes reducer actions to update redux state
export type AppDispatch = typeof store.dispatch;

export type RootState = ReturnType<typeof store.getState>;