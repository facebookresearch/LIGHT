import React, {useState, useEffect, useRef} from "react";

import TaskButton from "../TaskButton"
import { MdCancel } from "react-icons/md";

const AttributeRow = ({
    attribute,
    objectName,
    objectColor,
    isConstraint,
    updateHandler,
    deleteHandler
})=>{
    const [attributeName, setAttributeName] = useState("");
    const [attributeVal, setAttributeVal] = useState(true)
    const [isExistingAttribute, setIsExistingAttribute] = useState(false)

    useEffect(()=>{
        setAttributeName(attribute.name);
        setAttributeVal(attribute.val);
    },[])

    const changeHandler = e=>{
        e.preventDefault()
        console.log("CHANGE HANDLER WORKING", attribute, e.target.value)
        setAttributeName(e.target.value)
        updateHandler({name:e.target.value, val:attributeVal})
    }
    const trueHandler = ()=>{
        console.log("TRUE HANDLER WORKING")
        setAttributeVal(true)
        updateHandler({name:attributeName, val:true})
    }
    const falseHandler = ()=>{
        console.log("FALSE HANDLER WORKING")
        setAttributeVal(false)
        updateHandler({name:attributeName, val:false})
    }

    useEffect(()=>{
        console.log(attribute)
        const {name, val, isExisting} = attribute;
        setAttributeName(name)
        setAttributeVal(val)
        setIsExistingAttribute(isExisting)
    },[attribute])
    return(
        <div className="attributerow-container" >
            <div className="attribute-label__container ">
            {isConstraint?
            <p className="attribute-label__text"><span style={{fontWeight:"bold", color: objectColor}}>{objectName.toUpperCase()} </span></p>
            :
            <p className="attribute-label__text">Now the <span style={{fontWeight:"bold", color: objectColor}}>{objectName.toUpperCase()} </span></p>
            }
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
