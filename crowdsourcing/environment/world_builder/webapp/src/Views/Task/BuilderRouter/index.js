/* REACT */
import React, {useEffect, useState} from "react";
/* REDUX */
import { useAppDispatch, useAppSelector } from "../../../app/hooks";
import {updTaskRouterHistory, setTaskRouterCurrentLocation} from '../../../features/taskRouter/taskrouter-slice';

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
    // const currentLocation = useAppSelector((state) => state.taskRouter.currentLocation);
    // const builderRouterHistory = useAppSelector((state) => state.taskRouter.builderRouterHistory);
    // // REDUX DISPATCH FUNCTION
    // const dispatch = useAppDispatch();
    // /* ----REDUX ACTIONS---- */


    // /* ----LOCAL STATE---- */
    const [builderRouterCurrentLocation, setBuilderRouterCurrentLocation] = useState("/");
    const [builderRouterHistory, setBuilderRouterHistory] = useState([]);
    const builderRouterNavigate = (newLocation)=>{
        let oldLocation = builderRouterCurrentLocation;
        setBuilderRouterCurrentLocation(newLocation);
        let updatedRouterHistory = [...builderRouterHistory, oldLocation]
        setBuilderRouterHistory(updatedRouterHistory)
    }
    /* --- LIFE CYCLE FUNCTIONS --- */
    //Update location anytime Redux State Current Location Changes
    useEffect(()=>{
        window.localStorage.setItem("currentLocation", JSON.stringify("/"))
        window.localStorage.setItem("currentLocation", JSON.stringify("/"))
      },[currentLocation])

        // let formattedLocation="/"
        // let formattedLocationArray = currentLocation.split('/')
        // if(formattedLocationArray.length){
        //     formattedLocation= formattedLocationArray[formattedLocationArray.length-2]
        // }
    console.log("FORMATTED VIRTUAL LOCATION:  ", currentLocation)
    switch(builderRouterCurrentLocation) {
        case '/':
            return <MapPage2
                        api={api}
                        builderRouterNavigate={builderRouterNavigate}
                        currentLocation={builderRouterCurrentLocation}
                    />;
        case 'character':
            return <CharacterPage
                        api={api}
                        builderRouterNavigate={builderRouterNavigate}
                        currentLocation={builderRouterCurrentLocation}
                    />;
        case 'object':
            return <ObjectPage
                        api={api}
                        builderRouterNavigate={builderRouterNavigate}
                        currentLocation={builderRouterCurrentLocation}
                    />;
        case 'room':
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
