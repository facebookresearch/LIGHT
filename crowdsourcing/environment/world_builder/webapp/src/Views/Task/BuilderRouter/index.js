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
    const currentLocation = useAppSelector((state) => state.taskRouter.currentLocation);
    const builderRouterHistory = useAppSelector((state) => state.taskRouter.builderRouterHistory);
    // // REDUX DISPATCH FUNCTION
    // const dispatch = useAppDispatch();
    // /* ----REDUX ACTIONS---- */


    // /* ----LOCAL STATE---- */
    const [builderRouterCurrentLocation, setBuilderRouterCurrentLocation] = useState("");

    /* --- LIFE CYCLE FUNCTIONS --- */
    // Update location anytime Redux State Current Location Changes
    useEffect(()=>{
        console.log("CURRENT LOCATION IN ROUTER:  ", currentLocation)
        let formattedLocation="/"
        let formattedLocationArray = currentLocation.split('/')
        console.log("FORMATTED VIRTUAL LOCATION ARRAY:  ", formattedLocationArray)
        if(formattedLocationArray.length-1 !== ""){
            formattedLocation= formattedLocationArray[formattedLocationArray.length-2]
            console.log("FORMATTED LOCATION:  ", formattedLocation)
        }
        setBuilderRouterCurrentLocation(formattedLocation);
      },[currentLocation])

        // let formattedLocation="/"
        // let formattedLocationArray = currentLocation.split('/')
        // if(formattedLocationArray.length){
        //     formattedLocation= formattedLocationArray[formattedLocationArray.length-2]
        // }
    console.log("FORMATTED VIRTUAL LOCATION:  ", currentLocation)
    switch(builderRouterCurrentLocation) {
        case '/':
            return <MapPage2 api={api} />;
        case 'character':
            return <CharacterPage api={api} />;
        case 'object':
            return <ObjectPage api={api} />;
        case 'room':
            return <RoomPage api={api} />;
        default:
            return <MapPage2 api={api} />;
    }
}

export default BuilderRouter ;
