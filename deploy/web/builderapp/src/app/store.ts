//REDUX
import {configureStore} from "@reduxjs/toolkit";
//REDUCERS
import counterReducer from '../features/counter/counter-slice'

export const store = configureStore({
    reducer:{
        counter:counterReducer
    }
});

//TYPING DISPATCH ACTIONS
export type AppDispatch = typeof store.dispatch;
//TYPING OF STATE
export type RootState = ReturnType<typeof store.getState>;