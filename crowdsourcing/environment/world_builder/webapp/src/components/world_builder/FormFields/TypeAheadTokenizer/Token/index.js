/* REACT */
import React, { useRef, useState, useEffect } from 'react';
/* ---- REDUCER ACTIONS ---- */
import {  setTaskRouterCurrentLocation, updateTaskRouterHistory } from "../../../../../features/taskRouter/taskrouter-slice.ts";
/* TYPEAHEAD TOKENIZER */
import { Token as RBTToken } from 'react-bootstrap-typeahead';
/* ICONS */
import { BsGear } from 'react-icons/bs';
import { MdCancel } from "react-icons/md";

//Individual token in typeAhead Tokeenizer
const Token = ({
    index,
    option,
    roomId,
    sectionName,
    deleteTokenFunction,
    children
 }) => {
    /* ------ REDUX STATE ------ */
    //TASKROUTER
    const currentLocation = useAppSelector((state) => state.taskRouter.currentLocation);
    const taskRouterHistory = useAppSelector((state) => state.taskRouter.taskRouterHistory);
    /* REDUX DISPATCH FUNCTION */
    const dispatch = useAppDispatch();
    /* REDUX ACTIONS */
    const navigateToLocation = (nodeId)=>{
        let newLocation = `rooms/${roomId}/${sectionName}/${nodeId}`
        let updatedTaskRouterHistory = taskRouterHistory.push(newLocation)
        console.log("NEW LOCATION:   ", newLocation)
        console.log("UPDATED HISTORY:   ", updatedTaskRouterHistory)
        dispatch(updateTaskRouterHistory(updatedTaskRouterHistory))
        dispatch(setTaskRouterCurrentLocation(updatedTaskRouterHistory))
    }

    //LOCAL STATE AND REF
    const ref = useRef(null);
    const [tokenData, setTokenData] = useState({})
    /* REACT LIFECYCLE */
    useEffect(()=>{
        let updatedTokenData = {
            index: index,
            label: option.name,
            id:option.node_id
        }
        setTokenData(updatedTokenData)
    },[option])

    /* HANDLERS */
    const gearClickHandler = ()=>{
        navigateToLocation(`${option.data.node_id}`);
    }

    const deleteClickHandler = ()=>{
        console.log("TOKEN DATA:  ", option)
        deleteTokenFunction(option.key)
    }

    return (
        <span ref={ref}>
            <RBTToken
                index={index}
                option={tokenData}

            >
                {children}
                <BsGear color="black" onClick={gearClickHandler}/>
                <MdCancel color="red" onClick={deleteClickHandler}/>
            </RBTToken>
        </span>
    );
};

export default Token;
