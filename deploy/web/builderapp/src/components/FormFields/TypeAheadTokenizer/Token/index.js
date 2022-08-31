
/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React, { useRef, useState, useEffect } from 'react';
import { useParams, useRouteMatch, useHistory } from "react-router-dom";
/* TYPEAHEAD TOKENIZER */
import { Token as RBTToken } from 'react-bootstrap-typeahead';
/* ICONS */
import { BsGear } from 'react-icons/bs';
import { MdCancel } from "react-icons/md";

const Token = ({
    index,
    option,
    worldId,
    roomId,
    sectionName,
    deleteTokenFunction,
    children
 }) => {
    //REACT ROUTER
    const history = useHistory();
    
    const ref = useRef(null);
    const [tokenData, setTokenData] = useState({})

    useEffect(()=>{
        let updatedTokenData = {
            index: index,
            label: option.name,
            id:option.node_id
        }
        setTokenData(updatedTokenData)
    },[option])

    const gearClickHandler = ()=>{
        console.log("roomid", roomId)
        console.log(`/editworld/${worldId}/details/map/rooms/${roomId}/${sectionName}/${option.data.node_id}`)
        history.push(`/editworld/${worldId}/details/map/rooms/${roomId}/${sectionName}/${option.data.node_id}`);
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
