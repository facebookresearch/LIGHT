/* REACT */
import React, {useEffect, useState} from "react";
/* REDUX */
import { useAppDispatch, useAppSelector } from "../../app/hooks";
import {currentLocation, builderRouterHistory} from '../../../features/taskRouter';

/* STYLES */
import "./styles.css";
/* CUSTOM COMPONENTS */
import MapPage2 from "../../builder_pages/MapPage2";
import CharacterPage from "../../builder_pages/CharacterPage";
import ObjectPage from "../../builder_pages/ObjectPage";
import RoomPage from "../../builder_pages/RoomPage";

const BuilderRouter = ({virtualPath, api}) => {
    //REDUX STATE
    const currentLocation = useAppSelector((state) => state.taskRouter.currentLocation);
    const builderRouterHistory = useAppSelector((state) => state.taskRouter.builderRouterHistory);
    // REDUX DISPATCH FUNCTION
    const dispatch = useAppDispatch();
    /* ----REDUX ACTIONS---- */


    /* ----LOCAL STATE---- */
    const [builderRouterCurrentLocation, setBuilderRouterCurrentLocation] = useState("");

    const [worldData, setWorldData] = useState({})

    /* --- LIFE CYCLE FUNCTIONS --- */
    // Update location anytime Redux State Current Location Changes
    useEffect(()=>{
        setBuilderRouterCurrentLocation(currentLocation);
      },[currentLocation])

    const RenderPage = ()=> {
        let formattedLocation="/"
        let formattedLocationArray = currentLocation.split('/')
        if(formattedLocationArray.length){
            formattedLocation= formattedLocationArray[formattedLocationArray.length-2]
        }
        switch(builderRouterCurrentLocation) {
            case '/':
                return <MapPage2/>;
            case 'character':
                return <CharacterPage/>;
            case 'object':
                return <ObjectPage/>;
            case 'room':
                return <RoomPage/>;
            default:
                return <MapPage2/>;
        }
      }


  return <RenderPage/>;
}
