import React, {useState, useEffect, useRef} from "react";

import TaskButton from "../TaskButton"
import { MdCancel } from "react-icons/md";

const AttributeRow = ({attribute, objectName, objectColor, isConstraint})=>{
    const [attributeName, setAttributeName] = useState("");
    const [attributeVal, setAttributeVal] = useState(true)
    const [isExistingAttribute, setIsExistingAttribute] = useState(false)
    const nameRef = useRef();
    const changeHandler = e=>{
        e.preventDefault()

    }
    const trueHandler = ()=>{
        setAttributeVal(true)
    }
    const falseHandler = ()=>{
        setAttributeVal(false)
    }

    useEffect(()=>{
        const {name, val, isExisting} = attribute;
        setAttributeName(name)
        setAttributeVal(val)
        setIsExistingAttribute(isExisting)
    },[])
    return(
        <div className="row-container" >
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
                    ref={nameRef}
                    defaultValue={attributeName}
                    disabled={isExistingAttribute ? true : false}
                />
            </div>
            <MdCancel color="red" className="attribute-icon" />
        </div>
    )
}
export default AttributeRow;
