/* REDUX */
import { createSlice, PayloadAction } from "@reduxjs/toolkit";

interface LightMessage {
  id: number;
  message: string;
}

interface MessageListItem {
  id: number;
  data: LightMessage;
  key: any
}

/* STATE TYPE */
interface WorkerActivityState {
  counter: number;
  LightMessageList: Array<MessageListItem>;
}

/* Initial value of the state */
const initialState: WorkerActivityState = {
  counter: 0,
  LightMessageList:[]
};

const workerActivitySlice = createSlice({
  name: "workerActivity",
  initialState,
  /* REDUCER ACTIONS */
  reducers: {
    addMessage(state, action: PayloadAction<any>) {
      let newMessageList = action.payload;
      let updatedCounter = newMessageList.length;
      console.log("UPDATED MESSAGE LIST:  ", newMessageList)
      console.log("NEW MESSAGE:  ", newMessageList)
      return { ...state, counter: updatedCounter, LightMessageList: newMessageList };
    },
  },
});

/* EXPORTED REDUCER ACTIONS */
// import anywhere in app to use
export const { addMessage } = workerActivitySlice.actions;
/* SLICE REDUCER */
export default workerActivitySlice.reducer;
