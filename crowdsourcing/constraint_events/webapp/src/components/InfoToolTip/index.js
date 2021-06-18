import React, {useEffect, useState} from "react";

import "./styles.css";
import {Tooltip} from 'react-tippy';
// ICONS
import { BsInfoCircle } from "react-icons/bs";

//CUSTOM COMPONENTS
import Tip from "./Tip"

const InfoToolTip = ({tutorialCopy, children})=>{
    const [isHovering, setIsHovering] =useState(false)
    return (
    <div className="info-container">
        <div className="child-container">
            {children}
        </div>
        <Tooltip
            html={
            <Tip tutorialCopy={tutorialCopy}/>
            }
            position="left"
            theme="transparent"
        >
            <BsInfoCircle />
      </Tooltip>
    </div>
    )
}


export default InfoToolTip ;
