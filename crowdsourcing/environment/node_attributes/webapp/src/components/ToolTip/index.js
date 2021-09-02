//REACT
import React from "react";
//STYLES
import "./styles.css";
//BOOTSTRAP
import OverlayTrigger from 'react-bootstrap/OverlayTrigger';
import Tooltip from 'react-bootstrap/Tooltip';


//AttributeQuestions - Renders all default questions for a item type
const ToolTip = ({
    toolTipText,
    children
})=>{
    const renderTooltip = (props) => {
        console.log("TOOL TIP:  ", toolTipText)
        return (
        <Tooltip id="task-tooltip" {...props}>
          {toolTipText}
        </Tooltip>
        )
    };


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
export default ToolTip;
