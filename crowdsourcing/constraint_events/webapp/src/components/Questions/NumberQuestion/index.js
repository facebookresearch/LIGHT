//REACT
import React, {useEffect, useState, useRef} from "react";
//STYLING
import "./styles.css"

const NumberQuestion = ({question, formFunction})=>{
    const [formNumber, setFormNumber] = useState(0)
    useEffect(()=>{
        setDescription(formVal)
    },[])
    const changeHandler = e=>{
        e.preventDefault()
        setFormNumber(e.target.value)
        formFunction(description)
    }
    return(
        <div className="numberform-container" >
            <div className="numberanswer-container">
                <label for="limit"> {question} </label>
                <input
                    type="number"
                    id="limit"
                    name="limit"
                    min="1"
                    onChange={changeHandler}
                    value={formNumber}
                />

            </div>
        </div>
    )
}
export default NumberQuestion;
