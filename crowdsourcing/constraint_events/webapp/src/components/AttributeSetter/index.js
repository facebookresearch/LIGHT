import React, {useState, useEffect} from "react";

import "./styles.css"

import AttributeRow from "./AttributeRow"


const AttributeSetter = ({
    header,
    objectName,
    objectColor,
    attributes,
    isConstraint,
    setter
}) => {
    const [attributeList, setAttributeList] = useState([])
    useEffect(()=>{
        if(attributes){
        const existingAttributes = attributes.map(att => ({...att, isExisting:true}))
        setAttributeList(existingAttributes)
        }
    },[])
    const addAttributeHandler = ()=>{
        const newAtt = [...attributeList, {name:"", val:true}]
        setAttributeList(newAtt)
        setter(newAtt)
    }
    const updateAttributeHandler = (updateIndex, update) => {
        let updatedArr = attributeList.filter((item, index)=> (index !== updateIndex))
        updatedArr = [...updatedArr.filter, update]
        setAttributeList(updatedArr)
        setter(updatedArr)
    }
    const removeAttributeHandler = (deletedIndex)=>{
        let updatedArr = attributeList.filter((item, index)=> (index !== deletedIndex))
        setAttributeList(updatedArr)
        setter(updatedArr)
    }
    return (
        <div className="setter-container">
            <div className="setter-header">
                <div></div>
                <div className="label-container">
                    <p className="label-text">
                        <span style={{fontWeight:"bold", color: objectColor}}>{objectName.toUpperCase()}</span> {header}
                    </p>
                </div>
                <div className="button-container" onClick={addAttributeHandler}>
                    <p className="button-text">
                        +
                    </p>
                </div>
            </div>
            <div className="attributes-container">
                {
                  attributeList.length ?
                  attributeList.map((att, index)=>(
                      <AttributeRow
                        key={index}
                        objectName={objectName}
                        objectColor={objectColor}
                        attribute={att}
                        isConstraint={isConstraint}
                        updateHandler={(update)=>updateAttributeHandler(index, update)}
                        deleteHandler={()=>removeAttributeHandler(index)}
                    />
                  ))
                  :
                  null
                }
            </div>
        </div>
    );
}

export default AttributeSetter ;
