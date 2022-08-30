
/*****
 * Copyright (c) Meta Platforms, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

//REACT
import React, {useEffect, useState, useRef} from "react";
//STYLING
import "./styles.css"

//NumberQuestion - Question with number for answer.
const NumberQuestion = ({
    question, //Question Text
    formFunction // setState function that connects to payload state
})=>{
    //Local State
    const [formNumber, setFormNumber] = useState(0)

    //changeHandler - updates both local and payload state with answer
    const changeHandler = e=>{
        e.preventDefault();
        setFormNumber(e.target.value)
        formFunction(e.target.value)
    }

    useEffect(()=>{
        formFunction(formNumber)
    },[])
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
