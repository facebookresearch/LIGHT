import React, {useEffect, useRef} from "react";

//CUSTOM COMPONENTS
import DropdownSelect from "../../DropdownSelect";


const FieldRow = ({field, dropdown, options})=>{
    const answerRef = useRef();
    const changeHandler = e=>{
        e.preventDefault()

    }

    if(dropdown){

        return(
            <div className="fieldrow-container" >
                <div className="fieldrow-container__section--half" style={{justifyContent:"flex-end"}} >
                    <div className="field-container">
                        <p className="field-text">
                            {field}
                        </p>
                    </div>
                </div>
                <div className="fieldrow-container__section--half" style={{justifyContent:"flex-start"}}>
                    <DropdownSelect options={options} />
                </div>
            </div>
        )
    }else{
        return(
            <div className="fieldrow-container" >
                <div className="fieldrow-container__section--half" style={{justifyContent:"flex-end"}}>
                    <div className="field-container">
                        <p className="field-text">
                            {field}
                        </p>
                    </div>
                </div>
                <div className="fieldrow-container__section--half" style={{justifyContent:"flex-start"}} >
                    <div className="fieldanswer-container">
                        <input
                            className="fieldanswer-text"
                            ref={answerRef}
                        />
                    </div>
                </div>
            </div>
        )
    }
}
export default FieldRow;
