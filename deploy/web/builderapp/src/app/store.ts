//REDUX
import {configureStore} from "@reduxjs/toolkit";
//REDUCERS
import playerWorldsReducer from '../features/playerWorlds/playerworlds-slice';
import ModalReducer from '../features/modal/modal-slice';

export const store = configureStore({
    reducer:{
        playerWorlds: playerWorldsReducer,
        modal: ModalReducer
    }
});

//TYPING DISPATCH ACTIONS
export type AppDispatch = typeof store.dispatch;
//TYPING OF STATE
export type RootState = ReturnType<typeof store.getState>;