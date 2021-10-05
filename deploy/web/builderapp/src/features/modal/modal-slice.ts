/* REDUX */
import { createSlice, PayloadAction } from "@reduxjs/toolkit";

/* STATE TYPE */
interface ModalState {
  showModal: Boolean;
  modalType: String;
}

/* Initial value of the state */
const initialState: ModalState = {
    showModal: false,
    modalType: ""
};

//Create slice will generate action objects for us
const modalSlice = createSlice({
  name: "modal",
  initialState,
  /* REDUCER ACTIONS */
  reducers: {
        toggleModal(state, action: PayloadAction<ModalState>) {
            if(!state.showModal){
                return action.payload
            }else {
                return { showModal: false, modalType: "" }
            }
        },
    }
});

/* EXPORTED REDUCER ACTIONS */
// import anywhere in app to use
export const {
    toggleModal
} = modalSlice.actions;
/* SLICE REDUCER */
export default modalSlice.reducer;