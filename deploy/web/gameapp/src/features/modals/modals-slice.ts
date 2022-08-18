/* REDUX */
import { createSlice, PayloadAction } from "@reduxjs/toolkit";

/* STATE TYPE */
interface ModalState {
  showReportModal: boolean;
  reportModalMesssage: string;
  reportModalMessageId: string;
}

/* Initial value of the state */
const initialState: ModalState = {
  showReportModal: false,
  reportModalMesssage: "",
  reportModalMessageId: "",
};
//Create slice will generate action objects for us
const modalSlice = createSlice({
  name: "modals",
  initialState,
  /* REDUCER ACTIONS */
  reducers: {
    setReportModal(state, action: PayloadAction<boolean>) {
      return { ...state, showReportModal: action.payload };
    },
    setReportModalMesssage(state, action: PayloadAction<string>) {
      return { ...state, reportModalMesssage: action.payload };
    },
    setReportModalMessageId(state, action: PayloadAction<string>) {
      return { ...state, reportModalMessageId: action.payload };
    },
  },
});

/* EXPORTED REDUCER ACTIONS */
// import anywhere in app to use
export const {
  setReportModal,
  setReportModalMesssage,
  setReportModalMessageId,
} = modalSlice.actions;
/* SLICE REDUCER */
export default modalSlice.reducer;
