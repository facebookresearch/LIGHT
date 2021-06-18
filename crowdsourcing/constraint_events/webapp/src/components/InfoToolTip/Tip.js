import React, {useEffect, useState} from "react";

import {Tooltip} from 'react-tippy';
// ICONS
import { BsInfoCircle } from "react-icons/bs";

const Tip = ({tutorialCopy})=>{

    return (
        <>
            <p className="tip-text">
                {tutorialCopy}
            </p>
        </>
    )
}


export default Tip ;
