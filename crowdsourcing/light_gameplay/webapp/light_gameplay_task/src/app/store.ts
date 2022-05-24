import { configureStore } from '@reduxjs/toolkit'
//REDUCERS
import workerActivityReducer from "../features/workerActivity/workerActivity-slice";

export const store = configureStore({
  reducer: {
    workerActivity: workerActivityReducer,
  },
})


export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch
