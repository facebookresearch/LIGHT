//REDUX
import {configureStore} from "@reduxjs/toolkit";
//REDUCERS
import PlayerWorldsReducer from '../features/playerWorlds/playerworlds-slice';
import RoomsReducer from '../features/rooms/rooms-slice';
import CharacterReducer from '../features/characters/characters-slice';
import ObjectsReducer from '../features/objects/objects-slice';
import ModalReducer from '../features/modal/modal-slice';
import SideBarReducer from "../features/sidebars/sidebars-slice";

export const store = configureStore({
    reducer:{
        playerWorlds: PlayerWorldsReducer,
        worldRooms: RoomsReducer,
        worldCharacters: CharacterReducer,
        worldObjects: ObjectsReducer,
        modal: ModalReducer,
        sidebars: SideBarReducer
    }
});

//TYPING DISPATCH ACTIONS
export type AppDispatch = typeof store.dispatch;
//TYPING OF STATE
export type RootState = ReturnType<typeof store.getState>;