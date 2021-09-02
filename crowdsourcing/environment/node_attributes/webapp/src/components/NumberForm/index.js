//REACT
import React, {useEffect, useState} from "react";
//STYLING
import "./styles.css"
//CUSTOM COMPONENTS
import InfoIcon from "../Icons/Info";
import ToolTip from "../ToolTip/index.js"

//NumberQuestion - Question with number for answer.
const NumberForm = ({
    header, //Header Text
    formFunction, // setState function that connects to payload state
    startingVal, // initial value of form
    toolTip
})=>{
    /*---------- State ----------*/
    const [formNumber, setFormNumber] = useState(startingVal)

    //changeHandler - updates both local and payload state with answer
    const changeHandler = e=>{
        e.preventDefault()
        setFormNumber(e.target.value)
        formFunction(e.target.value)
    }

    useEffect(()=>{
        formFunction(formNumber)
    },[])
    return(
        <div className="numberform-container" >
            <div className="numberanswer-container">
                <div className="numberanswer-header">
                    <p className="numberanswer-header__text" >
                        {header}
                    </p>
                    <ToolTip
                        toolTipText={toolTip}
                    >
                        <div>
                            <InfoIcon dark={true}/>
                        </div>
                    </ToolTip>
                </div>
                <input
                    type="number"
                    id="limit"
                    name="limit"
                    min="1"
                    onChange={changeHandler}
                    value={formNumber}
                    className="numberanswer-input"
                />

            </div>
        </div>
    )
}
export default NumberForm;
