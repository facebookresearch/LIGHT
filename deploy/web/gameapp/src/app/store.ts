//REDUX
import { configureStore } from "@reduxjs/toolkit";
//REDUCERS
import personaReducer from "../features/playerInfo/persona-slice";
import locationReducer from "../features/playerInfo/location-slice";
import xpReducer from "../features/playerInfo/xp-slice";
import giftXpReducer from "../features/playerInfo/giftxp-slice";

export const store = configureStore({
  reducer: {
    persona: personaReducer,
    location: locationReducer,
    giftXp: giftXpReducer,
    xp: xpReducer,
  },
});

export type AppDispatch = typeof store.dispatch;
export type RootState = ReturnType<typeof store.getState>;
