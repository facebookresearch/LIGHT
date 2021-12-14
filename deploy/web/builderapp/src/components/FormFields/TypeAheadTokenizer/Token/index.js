/* REACT */
import React, { useRef, useState, useEffect } from 'react';
import { useParams, useRouteMatch, useHistory } from "react-router-dom";
/* REACT DND */
import { useDrag, useDrop } from 'react-dnd';
/* TYPEAHEAD TOKENIZER */
import { Token as RBTToken } from 'react-bootstrap-typeahead';
/* ICONS */
import { BsGear } from 'react-icons/bs';

const Token = ({
    index,
    option,
    worldId,
    roomId,
    sectionName,
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

    return (
        <span ref={ref}>
            <RBTToken
                index={index}
                option={tokenData}
            
            >
                {children}
                <BsGear onClick={gearClickHandler}/>
            </RBTToken>
        </span>
    );
};

export default Token;
