/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

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
