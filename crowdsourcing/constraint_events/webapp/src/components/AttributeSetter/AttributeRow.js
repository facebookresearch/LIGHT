import React, {useState, useEffect, useRef} from "react";

import TaskButton from "../TaskButton"

const AttributeRow = ({attribute})=>{
    const [attributeName, setAttributeName] = useState("");
    const [attributeVal, setAttributeVal] = useState(false)
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
        const {name, val} = attribute;
        setAttributeName(name)
        setAttributeVal(val)
    },[])
    return(
        <div className="row-container" >
            <div className="attribute-container">
                <input
                    className="name-text"
                    ref={nameRef}
                    defaultValue={attributeName}
                />
            </div>
            <div className="value-container">
                <TaskButton
                    name="TRUE"
                    isSelected={attributeVal}
                    selectFunction={trueHandler}
                    unselectedContainer="b-button__container true"
                    selectedContainer="b-selectedbutton__container true"
                    unselectedText="b-button__text true"
                    selectedText=" b-selectedbutton__text"

                    />
                <TaskButton
                    name="False"
                    isSelected={attributeVal===false}
                    selectFunction={falseHandler}
                    unselectedContainer="b-button__container false"
                    selectedContainer="b-selectedbutton__container false"
                    unselectedText="b-button__text false"
                    selectedText=" b-selectedbutton__text"
                />
            </div>
        </div>
    )
}
export default AttributeRow;
