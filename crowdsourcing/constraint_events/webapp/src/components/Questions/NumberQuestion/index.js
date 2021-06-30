//REACT
import React, {useEffect, useState, useRef} from "react";
//STYLING
import "./styles.css"

const NumberQuestion = ({question, formFunction})=>{
    const [formNumber, setFormNumber] = useState(0)
    useEffect(()=>{
        formFunction(formNumber)
    },[])
    const changeHandler = e=>{
        e.preventDefault()
        setFormNumber(e.target.value)
        formFunction(e.target.value)
    }
    return(
        <div className="numberform-container" >
            <div className="numberanswer-container">
                <p className="numberanswer-header" > {question} </p>
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
export default NumberQuestion;
