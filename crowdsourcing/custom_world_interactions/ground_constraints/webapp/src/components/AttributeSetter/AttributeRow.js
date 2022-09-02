import React, {useState, useEffect, useRef} from "react";

import TaskButton from "../TaskButton"
import { MdCancel } from "react-icons/md";
//AttributeRow - Tracks names and values for each attribute and allows used to edit the names and values with buttons assigning a boolean value and an input to change name of attribute
const AttributeRow = ({
    attribute,//Attribute object containing name and val keys
    objectName, //Name of Object
    objectColor, // Color of Object
    isConstraint, //Boolean value that alters text for each row.
    updateHandler, // Function that handles updates the attribute Array
    deleteHandler // Function that handles removing attributes from attribute Array
})=>{
    //Local state tracking and setting name and val of Attributes as well as whether or not attribute already existed prior to Task input.
    const [attributeName, setAttributeName] = useState(attribute.name);
    const [attributeVal, setAttributeVal] = useState(attribute.value);
    // const [attributeName, setAttributeName] = useState("");
    // const [attributeVal, setAttributeVal] = useState(true);
    //Sets Starting values of local state
    useEffect(()=>{
        setAttributeName(attribute.name);
        setAttributeVal(attribute.value);
    },[])
    //Updates Local and Payload state with changes to object name attribute
    const changeHandler = e=>{
        e.preventDefault()
        setAttributeName(e.target.value)
        updateHandler({...attribute, name:e.target.value, value:attributeVal})
    }
    //Sets Val attribute to true
    const trueHandler = ()=>{
        setAttributeVal(true)
        updateHandler({...attribute, name:attributeName, value:true})
    }
    //Sets Val attribute to true
    const falseHandler = ()=>{
        setAttributeVal(false);
        updateHandler({...attribute, name:attributeName, value:false});
    }

    useEffect(()=>{
        const {name, value, isExisting} = attribute;
        setAttributeName(name);
        setAttributeVal(value);
    },[attribute])
    return(
        <div className="attributerow-container" >
            <div className="attribute-label__container ">
                <p className="attribute-label__text">{isConstraint ? "": " Now the "}<span style={{fontWeight:"bold", color: objectColor}}>{objectName.toUpperCase()} </span></p>
            </div>
            <div className="value-container">
                {attributeVal ? <TaskButton
                    name={isConstraint ? " MUST BE ":" IS "}
                    isSelected={attributeVal}
                    selectFunction={() => {}}
                    unselectedContainer="b-button__container true"
                    selectedContainer="b-selectedbutton__container true"
                    unselectedText="b-button__text true"
                    selectedText=" b-selectedbutton__text"
                    disabled={true}
                    /> : 
                <TaskButton
                    name={isConstraint ? " MUST NOT BE ":" IS NOT "}
                    isSelected={attributeVal===false}
                    selectFunction={() => {}}
                    unselectedContainer="b-button__container false"
                    selectedContainer="b-selectedbutton__container false"
                    unselectedText="b-button__text false"
                    selectedText=" b-selectedbutton__text"
                    disabled={true}
                />}
            </div>
            <div className="attribute-container">
                <div className="name-text" style={{borderStyle:"none" }}>{attributeName}</div>

                {/* <input
                    className="name-text"
                    onChange={changeHandler}
                    value={attributeName}
                    disabled={true}
                /> */}
            </div>
            {/* <MdCancel onClick={deleteHandler} color="red" className="attribute-icon" /> */}
        </div>
    )
}
export default AttributeRow;
