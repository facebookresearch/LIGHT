//REDUX
import { configureStore } from "@reduxjs/toolkit";
//REDUCERS
import agentsReducer from "../features/agents/agents-slice";
import giftXpReducer from "../features/playerInfo/giftxp-slice";
import locationReducer from "../features/playerInfo/location-slice";
import messagesReducer from "../features/messages/messages-slice";
import personaReducer from "../features/playerInfo/persona-slice";
import xpReducer from "../features/playerInfo/xp-slice";

export const store = configureStore({
  reducer: {
    agents: agentsReducer,
    giftXp: giftXpReducer,
    location: locationReducer,
    messages: messagesReducer,
    persona: personaReducer,
    xp: xpReducer,
  },
});

export type AppDispatch = typeof store.dispatch;
export type RootState = ReturnType<typeof store.getState>;
