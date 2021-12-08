import React, { useRef, useState, useEffect } from 'react';
import { useDrag, useDrop } from 'react-dnd';
import { Token as RBTToken } from 'react-bootstrap-typeahead';

import { BsGear } from 'react-icons/bs';

const Token = ({
    index,
    option,
    children
 }) => {
    
    const ref = useRef(null);
    const [tokenData, setTokenData] = useState({})

    useEffect(()=>{
        let updatedTokenData = {
            index: index,
            label: option.name
        }
        setTokenData(updatedTokenData)
    },[option])

    return (
        <span ref={ref}>
            <RBTToken
                index={index}
                option={tokenData}
            
            >
            {children}
            <BsGear/>
            </RBTToken>
        </span>
    );
};

export default Token;
