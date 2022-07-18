//REDUX
import {configureStore} from "@reduxjs/toolkit";
//REDUCERS
import ErrorReducer from '../features/errors/errors-slice';
import LoadingReducer from '../features/loading/loading-slice';
import PlayerWorldReducer from '../features/playerWorld/playerworld-slice';
import RoomsReducer from '../features/rooms/rooms-slice';
import CharacterReducer from '../features/characters/characters-slice';
import ObjectsReducer from '../features/objects/objects-slice';
import MapReducer from "../features/map/map-slice";
import ModalReducer from '../features/modal/modal-slice';
import SideBarReducer from "../features/sidebars/sidebars-slice";
import TaskRouterReducer from "../features/taskRouter/taskrouter-slice"

export const store = configureStore({
    reducer:{
        errors: ErrorReducer,
        loading:LoadingReducer,
        playerWorld: PlayerWorldReducer,
        map: MapReducer,
        modal: ModalReducer,
        sidebars: SideBarReducer,
        taskRouter: TaskRouterReducer,
        worldCharacters: CharacterReducer,
        worldObjects: ObjectsReducer,
        worldRooms: RoomsReducer
    }
});

//TYPING DISPATCH ACTIONS
export type AppDispatch = typeof store.dispatch;
//TYPING OF STATE
export type RootState = ReturnType<typeof store.getState>;
