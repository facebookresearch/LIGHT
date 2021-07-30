import React, {useEffect, useRef} from "react";

import TipsCopy from "./TipsCopy"

const DescriptionForm = ({formVal, formFunction})=>{
    const changeHandler = e=>{
        e.preventDefault()
        formFunction(e.target.value)

    }
    return(
        <div className="form-container" >
            <h1 className="form-header">
                Description
            </h1>
            <div className="tip-container">
            {
                TipsCopy ?
                TipsCopy.map((tip, index) => (
                <p className="form-tip" key={index}>
                    <span style={{fontWeight:"bold"}} >* </span>{tip}
                </p>
                ))
                :
                null
            }
            </div>
            <textarea
                className="description-form"
                onChange={changeHandler}
                value={formVal}
                rows="7"
                type="text"
                placeholder="Describe the interaction between these two objects (Remember to commit to the medieval fantasy setting) - Start with 'You...'"
            />
        </div>
    )
}
export default DescriptionForm;
