import React, {useState, useEffect} from "react";

import "./styles.css"

import AttributeRow from "./AttributeRow"


const AttributeSetter = ({header, objectName, objectColor, attributes}) => {
    const [attributeList, setAttributeList] = useState([])
    useEffect(()=>{
        if(attributes){
        setAttributeList(attributes)
        }
    },[attributes])
    const addAttributeHandler = ()=>{
        const newAtt = [...attributeList, {name:"", val:false}]
        setAttributeList(newAtt)
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
                      <AttributeRow key={index} attribute={att} />
                  ))
                  :
                  null
                }
            </div>
        </div>
    );
}

export default AttributeSetter ;
