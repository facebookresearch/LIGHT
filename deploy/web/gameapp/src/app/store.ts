//REDUX
import { configureStore } from "@reduxjs/toolkit";
//REDUCERS
import agentsReducer from "../features/agents/agents-slice";
import giftXpReducer from "../features/playerInfo/giftxp-slice";
import locationReducer from "../features/playerInfo/location-slice";
import messagesReducer from "../features/messages/messages-slice";
import personaReducer from "../features/playerInfo/persona-slice";
import sessionXpReducer from "../features/sessionInfo/sessionxp-slice";
import sessionSpentGiftXpReducer from "../features/sessionInfo/sessionspentgiftxp-slice";
import xpReducer from "../features/playerInfo/xp-slice";

//Store - Redux store that as a "bank" of state components can subscribe to
export const store = configureStore({
  //Combined reducer of all slices
  reducer: {
    agents: agentsReducer,
    giftXp: giftXpReducer,
    location: locationReducer,
    messages: messagesReducer,
    persona: personaReducer,
    sessionXp: sessionXpReducer,
    sessionSpentGiftXp: sessionSpentGiftXpReducer,
    xp: xpReducer,
  },
});

// AppDispatch - function that that takes reducer actions to update redux state
export type AppDispatch = typeof store.dispatch;

export type RootState = ReturnType<typeof store.getState>;
