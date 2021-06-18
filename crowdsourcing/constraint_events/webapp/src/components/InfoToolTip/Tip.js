import React, {useEffect, useState} from "react";

import {Tooltip} from 'react-tippy';
// ICONS
import { BsInfoCircle } from "react-icons/bs";

const Tip = ({tutorialCopy})=>{

    return (
        <div className="tip-container">
            <p className="tip-text">
                {tutorialCopy}
            </p>
        </div>
    )
}


export default Tip ;
