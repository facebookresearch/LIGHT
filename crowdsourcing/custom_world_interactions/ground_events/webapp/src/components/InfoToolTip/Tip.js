//REACT
import React from "react";

// Tip - html rendered by tool tip
const Tip = ({
    tutorialCopy//Text that will be displayed in the tool tip
})=>{
    return (
        <div className="tip-container">
            <p className="tip-text">
                {tutorialCopy}
            </p>
        </div>
    )
}

export default Tip ;
