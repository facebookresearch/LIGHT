/* REDUX */
import { createSlice, PayloadAction } from "@reduxjs/toolkit";

/* STATE TYPE */
interface PersonaState {
  description: string;
  giftXp: number;
  id: string;
  name: string;
  prefix: string;
  xp: number;
}

/* Initial value of the state */
const initialState: PersonaState = {
  description: "",
  giftXp: 0,
  id: "",
  name: "",
  prefix: "",
  xp: 0,
};

//Create slice will generate action objects for us
const personaSlice = createSlice({
  name: "persona",
  initialState,
  /* REDUCER ACTIONS */
  reducers: {
    updatePersona(state, action: PayloadAction<PersonaState>) {
      return { ...state, ...action.payload };
    },
  },
});

/* EXPORTED REDUCER ACTIONS */
// import anywhere in app to use
export const { updatePersona } = personaSlice.actions;
/* SLICE REDUCER */
export default personaSlice.reducer;
