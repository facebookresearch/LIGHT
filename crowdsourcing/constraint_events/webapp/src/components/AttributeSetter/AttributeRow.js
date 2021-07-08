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
    const [attributeName, setAttributeName] = useState("");
    const [attributeVal, setAttributeVal] = useState(true)
    const [isExistingAttribute, setIsExistingAttribute] = useState(false)
    //Sets Starting values of local state
    useEffect(()=>{
        setAttributeName(attribute.name);
        setAttributeVal(attribute.val);
    },[])
    //Updates Local and Payload state with changes to object name attribute
    const changeHandler = e=>{
        e.preventDefault()
        setAttributeName(e.target.value)
        updateHandler({name:e.target.value, val:attributeVal})
    }
    //Sets Val attribute to true
    const trueHandler = ()=>{
        setAttributeVal(true)
        updateHandler({name:attributeName, val:true})
    }
    //Sets Val attribute to true
    const falseHandler = ()=>{
        setAttributeVal(false)
        updateHandler({name:attributeName, val:false})
    }

    useEffect(()=>{
        const {name, val, isExisting} = attribute;
        setAttributeName(name)
        setAttributeVal(val)
        setIsExistingAttribute(isExisting)
    },[attribute])
    return(
        <div className="attributerow-container" >
            <div className="attribute-label__container ">
                <p className="attribute-label__text">{isConstraint?"Now the":"" }<span style={{fontWeight:"bold", color: objectColor}}>{objectName.toUpperCase()} </span></p>
            </div>
            <div className="value-container">
                <TaskButton
                    name={isConstraint? "MUST BE":"IS "}
                    isSelected={attributeVal}
                    selectFunction={trueHandler}
                    unselectedContainer="b-button__container true"
                    selectedContainer="b-selectedbutton__container true"
                    unselectedText="b-button__text true"
                    selectedText=" b-selectedbutton__text"

                    />
                <TaskButton
                    name={isConstraint? "MUST NOT BE":"IS NOT"}
                    isSelected={attributeVal===false}
                    selectFunction={falseHandler}
                    unselectedContainer="b-button__container false"
                    selectedContainer="b-selectedbutton__container false"
                    unselectedText="b-button__text false"
                    selectedText=" b-selectedbutton__text"
                />
            </div>
            <div className="attribute-container">
                <input
                    className="name-text"
                    onChange={changeHandler}
                    value={attributeName}
                    disabled={isExistingAttribute ? true : false}
                />
            </div>
            <MdCancel onClick={deleteHandler} color="red" className="attribute-icon" />
        </div>
    )
}
export default AttributeRow;
