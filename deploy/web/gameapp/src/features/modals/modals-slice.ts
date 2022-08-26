/* REDUX */
import { createSlice, PayloadAction } from "@reduxjs/toolkit";

/* STATE TYPE */
interface ModalState {
  showReportModal: boolean;
  reportModalMessage: string;
  reportModalMessageId: string;
  reportModalActor: string;
  reportModalSubmitted: boolean;
}

/* Initial value of the state */
const initialState: ModalState = {
  showReportModal: false,
  reportModalMessage: "",
  reportModalMessageId: "",
  reportModalActor: "",
  reportModalSubmitted: false,
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
    setReportModalMessage(state, action: PayloadAction<string>) {
      return { ...state, reportModalMessage: action.payload };
    },
    setReportModalMessageId(state, action: PayloadAction<string>) {
      return { ...state, reportModalMessageId: action.payload };
    },
    setReportModalActor(state, action: PayloadAction<string>) {
      return { ...state, reportModalActor: action.payload };
    },
    setReportModalSubmitted(state, action: PayloadAction<boolean>) {
      return { ...state, reportModalSubmitted: action.payload };
    },
  },
});

/* EXPORTED REDUCER ACTIONS */
// import anywhere in app to use
export const {
  setReportModal,
  setReportModalMessage,
  setReportModalMessageId,
  setReportModalActor,
  setReportModalSubmitted,
} = modalSlice.actions;
/* SLICE REDUCER */
export default modalSlice.reducer;
