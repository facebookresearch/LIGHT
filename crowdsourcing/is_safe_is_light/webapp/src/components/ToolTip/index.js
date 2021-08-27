//REACT
import React, {useEffect, useState} from "react";
//STYLING
import "./styles.css";
//REACT TIPPY
import {Tooltip} from 'react-tippy';
// ICONS
import { BsInfoCircle } from "react-icons/bs";
//CUSTOM COMPONENTS
import Tip from "./Tip"


// InfoToolTip - renders an info icon that will display tooltip copy provided by props if has tooltip boolean value is true.  Other wise it will plainly render the child component
const InfoToolTip = ({
    hasToolTip,//Boolean value stating whether child component has tool tip or not.
    tipText, //  Tool Tip Copy passed as string
    children //  JSX next to tooltip
})=>{

    if(hasToolTip){
    return (
        <div className="info-container">
            <div className="child-container">
                {children}
            </div>
            <Tooltip
                html={
                <Tip tipText={tipText}/>
                }
                position="left"
                theme="dark"
                size="big"
            >
                <BsInfoCircle className="info-icon" />
            </Tooltip>
        </div>
    )}else{
        return <>{children}</>
    }
}


export default InfoToolTip ;
