import React, {useEffect, useRef} from "react";



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
        <p >

        </p>
            <textarea
                className="description-form"
                onChange={changeHandler}
                value={formVal}
                rows="5"
                type="text"
                placeholder="Describe the interaction between these two objects (Remember to commit to the medieval fantasy setting) - Start with 'You...'"
            />
        </div>
    )
}
export default DescriptionForm;
