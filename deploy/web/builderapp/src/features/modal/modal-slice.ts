
/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

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
        setModal(state, action: PayloadAction<ModalState>) {
            return action.payload
        },
    }
});

/* EXPORTED REDUCER ACTIONS */
// import anywhere in app to use
export const {
    setModal,
} = modalSlice.actions;
/* SLICE REDUCER */
export default modalSlice.reducer;