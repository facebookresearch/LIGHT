/* REACT */
import React, {useEffect, useState} from "react";
/* REDUX */
import { useAppDispatch, useAppSelector } from "../../../app/hooks";
import {updateTaskRouterHistory, setTaskRouterCurrentLocation} from '../../../features/taskRouter/taskrouter-slice';
/* STYLES */
import "./styles.css";
/* CUSTOM COMPONENTS */
import MapPage from "../../builder_pages/MapPage";
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
    //builderRouterNavigate - handles navigation to new locatinos and modifies the router history accordingly
    //each time this function is invoked it will add the previous currentLocation object to the end of the history array
    const builderRouterNavigate = (newLocation)=>{
        let oldLocation = builderRouterCurrentLocation;
        let updatedRouterHistory = [...builderRouterHistory, oldLocation]
        dispatch(updateTaskRouterHistory(updatedRouterHistory));
        dispatch(setTaskRouterCurrentLocation(newLocation));
    }

    /* ----LOCAL STATE---- */
    const [builderRouterPath, setBuilderRouterPath]= useState({name: "map", id: null});

    /* --- LIFE CYCLE FUNCTIONS --- */
    //Update location anytime Redux State Current Location Changes
    useEffect(()=>{
        let updatedBuilderRouterPath = builderRouterCurrentLocation.name
        setBuilderRouterPath(updatedBuilderRouterPath);
    },[builderRouterCurrentLocation])

    //Switch Case acts as a router for app using the name key of the current location to determine which page to render
    switch(builderRouterPath) {
        case 'map':
            return <MapPage
                        api={api}
                        builderRouterNavigate={builderRouterNavigate}
                    />;
        case 'characters':
            return <CharacterPage
                        api={api}
                        builderRouterNavigate={builderRouterNavigate}
                    />;
        case 'objects':
            return <ObjectPage
                        api={api}
                        builderRouterNavigate={builderRouterNavigate}
                    />;
        case 'rooms':
            return <RoomPage
                        api={api}
                        builderRouterNavigate={builderRouterNavigate}
                    />;
        default:
            return <MapPage2
                        api={api}
                        builderRouterNavigate={builderRouterNavigate}
                    />;
    }
}

export default BuilderRouter ;
