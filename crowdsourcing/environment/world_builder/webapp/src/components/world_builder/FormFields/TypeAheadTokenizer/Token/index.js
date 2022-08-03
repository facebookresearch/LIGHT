/* REACT */
import React, { useRef, useState, useEffect } from 'react';
/* REDUX */
import {useAppDispatch, useAppSelector} from '../../../../../app/hooks';
/* TYPEAHEAD TOKENIZER */
import { Token as RBTToken } from 'react-bootstrap-typeahead';
/* ICONS */
import { BsGear } from 'react-icons/bs';
import { MdCancel } from "react-icons/md";

//NOTE: ASK JACK ABOUT GEAR FUNCTION

//Individual token in typeAhead Tokeenizer
const Token = ({
    index,
    option,
    sectionName,
    deleteTokenFunction,
    builderRouterNavigate,
    children
 }) => {
    /* ------ REDUX STATE ------ */
    //TASKROUTER
    // const currentLocation = useAppSelector((state) => state.taskRouter.currentLocation);
    // const taskRouterHistory = useAppSelector((state) => state.taskRouter.taskRouterHistory);
    /* REDUX DISPATCH FUNCTION */
    // const dispatch = useAppDispatch();
    /* REDUX ACTIONS */
    //LOCAL STATE AND REF
    const ref = useRef(null);
    const [tokenData, setTokenData] = useState({})
    /* REACT LIFECYCLE */
    useEffect(()=>{
        let updatedTokenData = {
            index: index,
            label: option.name,
            id: option.node_id
        }
        setTokenData(updatedTokenData)
    },[option])

    /* HANDLERS */
    const gearClickHandler = ()=>{
        const gearLocation = {
            name: sectionName,
            id: option.data.node_id
        }
        builderRouterNavigate(gearLocation);
    }

    const deleteClickHandler = ()=>{
        deleteTokenFunction(option.key)
    }

    return (
        <span key={tokenData.id} ref={ref}>
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
