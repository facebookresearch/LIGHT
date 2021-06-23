import React, {useEffect, useState} from "react";

//CUSTOM COMPONENTS
import DropdownSelect from "../../DropdownSelect";


const FieldRow = ({field, dropdown, options, changeFunction, formState})=>{
    const [fieldVal, setFieldVal] = useState("")
    const changeHandler = e=>{
        e.preventDefault()
        console.log("FIELD UPDATE", field, ":   ", e.target.value)
        setFieldVal(e.target.value)
        changeFunction(e.target.value)
    }

    if(dropdown){

        return(
            <div className="fieldrow-container" >
                <div className="fieldrow-container__section--half" style={{justifyContent:"flex-end"}} >
                    <div className="field-container">
                        <p className="field-text">
                            {field.name.toUpperCase()}
                        </p>
                    </div>
                </div>
                <div className="fieldrow-container__section--half" style={{justifyContent:"flex-start"}}>
                    <DropdownSelect
                        options={options}
                        selectFunction={changeHandler}
                    />
                </div>
            </div>
        )
    }else{
        return(
            <div className="fieldrow-container" >
                <div className="fieldrow-container__section--half" style={{justifyContent:"flex-end"}}>
                    <div className="field-container">
                        <p className="field-text">
                            {field.name.toUpperCase()}
                        </p>
                    </div>
                </div>
                <div className="fieldrow-container__section--half" style={{justifyContent:"flex-start"}} >
                    <div className="fieldanswer-container">
                        <input
                            className="fieldanswer-text"
                            onChange={changeHandler}
                            value={fieldVal}
                        />
                    </div>
                </div>
            </div>
        )
    }
}
export default FieldRow;
