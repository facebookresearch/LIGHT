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
    const renderTooltip = (props) => (
        <Tooltip id="button-tooltip" {...props}>
          {toolTipText}
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
export default ToolTip;
