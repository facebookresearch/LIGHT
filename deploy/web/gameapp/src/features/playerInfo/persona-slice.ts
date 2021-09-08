//REDUX
import { createSlice, PayloadAction } from "@reduxjs/toolkit";

/* TYPING THE STATE */
interface PersonaState {
  description: string;
  giftXp: number;
  id: string;
  name: string;
  prefix: string;
  xp: number;
}

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
    //immer will handle immutability in state changess
    updatePersona(state, action: PayloadAction<PersonaState>) {
      return { ...state, ...action.payload };
    },
  },
});

export const { updatePersona } = personaSlice.actions;
export default personaSlice.reducer;
