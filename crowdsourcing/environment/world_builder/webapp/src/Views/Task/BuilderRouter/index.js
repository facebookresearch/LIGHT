/* REACT */
import React, {useEffect, useState} from "react";
/* REDUX */
import { useAppDispatch, useAppSelector } from "../../../app/hooks";
import {updateTaskRouterHistory, setTaskRouterCurrentLocation} from '../../../features/taskRouter/taskrouter-slice';

/* STYLES */
import "./styles.css";
/* CUSTOM COMPONENTS */
import MapPage2 from "../../../Views/builder_pages/MapPage2";
import CharacterPage from "../../../Views/builder_pages/CharacterPage";
import ObjectPage from "../../../Views/builder_pages/ObjectPage";
import RoomPage from "../../../Views/builder_pages/RoomPage";

const BuilderRouter = ({
    api
}) => {
    //REDUX STATE
    const builderRouterCurrentLocation = useAppSelector((state) => state.taskRouter.currentLocation);
    const builderRouterHistory = useAppSelector((state) => state.taskRouter.taskRouterHistory);
    // REDUX DISPATCH FUNCTION
    const dispatch = useAppDispatch();
    // /* ----REDUX ACTIONS---- */


    // /* ----LOCAL STATE---- */
    const [builderRouterPath, setBuilderRouterPath]= useState({name: "home", id: null});

    /* HANDLERS */
    const builderRouterNavigate = (newLocation)=>{
        let oldLocation = builderRouterCurrentLocation;
        dispatch(setTaskRouterCurrentLocation(newLocation));
        let updatedRouterHistory = [...builderRouterHistory, oldLocation]
        dispatch(updTaskRouterHistory(updatedRouterHistory));
    }
    /* --- LIFE CYCLE FUNCTIONS --- */
    //Update location anytime Redux State Current Location Changes
    useEffect(()=>{
        // let currentLocationArray = builderRouterCurrentLocation.split("/");
        // if(builderRouterHistory.length){
        //     let updatedHistory = [...builderRouterHistory, builderRouterCurrentLocation];
        //     for(let i = updatedHistory.length-1 ; i>=0 ; i--){

        //         let locationArray = updatedHistory[i].split("/");
        //         let currentSection = locationArray[0];
        //         if(currentSection == "rooms"){
        //             newRoomId = locationArray[1]
        //         }else if(currentSection == "characters"){
        //             newCharId = locationArray[1]
        //         }else if(currentSection == "objects"){
        //             newObjectId = locationArray[1]
        //         }
        //     }
        //     setRoomId(newRoomId);
        //     setCharacterId(newCharId);
        //     setObjectId(newObjectId);
        // }
        let updatedBuilderRouterPath = builderRouterCurrentLocation.locationName
        console.log("FORMATED PATH IN BUILDER ROUTER:  ", currentLocationArray[currentLocationArray.length-2])
        let updatedHistory = [...builderRouterHistory, builderRouterCurrentLocation];
        console.log("UPDATED ROUTER HISTORY:  ", updatedHistory)
        dispatch(updateTaskRouterHistory(updatedHistory));
        setBuilderRouterPath(updatedBuilderRouterPath)
    },[builderRouterCurrentLocation])

    switch(builderRouterPath) {
        case 'home':
            return <MapPage2
                        api={api}
                        builderRouterNavigate={builderRouterNavigate}
                        currentLocation={builderRouterCurrentLocation}
                    />;
        case 'characters':
            return <CharacterPage
                        api={api}
                        builderRouterNavigate={builderRouterNavigate}
                        currentLocation={builderRouterCurrentLocation}
                    />;
        case 'objects':
            return <ObjectPage
                        api={api}
                        builderRouterNavigate={builderRouterNavigate}
                        currentLocation={builderRouterCurrentLocation}
                    />;
        case 'rooms':
            return <RoomPage
                        api={api}
                        builderRouterNavigate={builderRouterNavigate}
                        currentLocation={builderRouterCurrentLocation}
                    />;
        default:
            return <MapPage2
                        api={api}
                        builderRouterNavigate={builderRouterNavigate}
                        currentLocation={builderRouterCurrentLocation}
                    />;
    }
}

export default BuilderRouter ;
