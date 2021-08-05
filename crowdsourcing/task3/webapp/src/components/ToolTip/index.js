//REACT
import React, {useState, useEffect, useRef} from "react";
//STYLES
import "./styles.css";
//BOOTSTRAP
import OverlayTrigger from 'react-bootstrap/OverlayTrigger';
import Tooltip from 'react-bootstrap/Tooltip';


// AttributeQuestions - Renders all default questions for a item type
const AttributeQuestions = ({
    toolTipText,
    children
})=>{
    const renderTooltip = (props) => (
        <Tooltip id="button-tooltip" {...props}>
          {description}
        </Tooltip>
      );


    return(
        <>
            <OverlayTrigger
                placement="top"
                delay={{ show: 250, hide: 400 }}
                overlay={renderTooltip}
            >
                {children}
            </OverlayTrigger>
        </>
    )
}
export default AttributeQuestions;
