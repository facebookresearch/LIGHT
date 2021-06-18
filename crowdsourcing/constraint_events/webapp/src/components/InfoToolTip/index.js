import React, {useEffect, useState} from "react";

import {Tooltip} from 'react-tippy';
// ICONS
import { BsInfoCircle } from "react-icons/bs";

const InfoToolTip = ({tutorialCopy, children})=>{
    const [isHovering, setIsHovering] =useState(false)

    return (
    <div className="info-container">
        {children}
        <Tooltip
            title={tutorialCopy}
            position="left"
        >
            <BsInfoCircle className={isHovering ? "info-hover" : "info"} onMouseEnter={()=>setIsHovering(true)} onMouseLeave={()=>setIsHovering(false)}/>
      </Tooltip>
    </div>
    )
}


export default InfoToolTip ;
