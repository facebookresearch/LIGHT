import React, {useEffect, useRef} from "react";

//CUSTOM COMPONENTS
import DropdownSelect from "../../DropdownSelect";


const FieldRow = ({field, dropdown, options})=>{
    const answerRef = useRef();
    const changeHandler = e=>{
        e.preventDefault()

    }

    if(dropdown){
        <div className="row-container" >
            <div className="field-container">
                <p className="field-text">
                    {field}
                </p>
            </div>
            <div className="answer-container">
                <DropdownSelect options={options} />
            </div>
        </div>
    }else{
        return(
            <div className="row-container" >
                <div className="field-container">
                    <p className="field-text">
                        {field}
                    </p>
                </div>
                <div className="answer-container">
                    <input
                        className="answer-text"
                        ref={answerRef}
                    />
                </div>
            </div>
        )
    }
}
export default FieldRow;
