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
    const [builderRouterPath, setBuilderRouterPath]= useState({name: "map", id: null});

    /* HANDLERS */
    const builderRouterNavigate = (newLocation)=>{
        console.log("NEW LOCATION DURING NAVIGATION::  ", newLocation)
        let oldLocation = builderRouterCurrentLocation;
        console.log("OLD LOCATION DURING NAVIGATION:  ", oldLocation)
        let updatedRouterHistory = [...builderRouterHistory, oldLocation]
        console.log("UPDATED HISTORY DURING NAVIGATION:  ", updatedRouterHistory)
        dispatch(updateTaskRouterHistory(updatedRouterHistory));
        dispatch(setTaskRouterCurrentLocation(newLocation));
    }
    /* --- LIFE CYCLE FUNCTIONS --- */
    //Update location anytime Redux State Current Location Changes
    useEffect(()=>{
        let updatedBuilderRouterPath = builderRouterCurrentLocation.name
        console.log("CURRENT LOCATION PATH!:  ", updatedBuilderRouterPath)
        setBuilderRouterPath(updatedBuilderRouterPath);
    },[builderRouterCurrentLocation])

    switch(builderRouterPath) {
        case 'map':
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
