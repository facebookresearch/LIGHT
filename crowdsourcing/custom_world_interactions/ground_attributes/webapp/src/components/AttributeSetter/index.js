
/*****
 * Copyright (c) Meta Platforms, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

//REACT
import React, {useState, useEffect} from "react";
//STYLING
import "./styles.css"
//CUSTOM COMPONENTS
import AttributeRow from "./AttributeRow"
import InfoToolTip from "../InfoToolTip";
//ICONS
import { AiOutlinePlus } from "react-icons/ai";
//Allows user to add and  set value of attributes
const AttributeSetter = ({
    header, // Label of setter
    objectName, //  Name of object to whom the Attributes belong
    objectColor, //  Text color of object
    attributes,  //  Array of attributes taken from target object
    isConstraint,  // Formats component for constraint case where attributes in place cannot be changed but can still be removed.
    setter, // The setState function that connects the values in Attributes Array to the payload being submitted
    toolTipCopy, //  Copy for relevant tooltip
    hasToolTip // signifies whether the component has a tooltip or not.
}) => {
    //Local State for Attributes being listed and changed in component
    const [attributeList, setAttributeList] = useState([])
    //Sets is existing attribute for attributes that already exist before interaction
    useEffect(()=>{
        if(attributes){
        // const existingAttributes = attributes.map(att => ({...att, isExisting:true}))
        const existingAttributes = attributes.map(att => ({...att, isExisting:false}))
        setAttributeList(existingAttributes)
        }
    },[])
    //Function used to add a "blank attribute to the array."
    const addAttributeHandler = ()=>{
        const newAtt = [...attributeList, {name:"", value:true}]
        setAttributeList(newAtt)
        setter(newAtt)
    }
    //Function used to update attributes
    const updateAttributeHandler = (updateIndex, update) => {
        // update attribute at given index, used to reorder but now does in-place
        let updatedArr = attributeList.map((value, i) => {return i === updateIndex ? update : value});
        setAttributeList(updatedArr) // Array with updated entry set to local state
        setter(updatedArr) // Array with updated entry set to payload state
    }
    //Function used to remove Attributes
    const removeAttributeHandler = (deletedIndex)=>{
        let updatedArr = attributeList.filter((item, index)=> (index !== deletedIndex))
        setAttributeList(updatedArr)
        setter(updatedArr)
    }
    return (
        <div className="setter-container">
            <InfoToolTip tutorialCopy={toolTipCopy} hasToolTip={hasToolTip}>
                <div className="setter-header">
                    <div></div>
                    <div className="label-container">
                        <p className="label-text">
                            <span style={{fontWeight:"bold", color: objectColor}}>
                                {objectName.toUpperCase()}
                            </span> {header}
                        </p>
                    </div>
                    <div className="button-container" onClick={addAttributeHandler}>
                        <AiOutlinePlus/>
                    </div>
                </div>
            </InfoToolTip>
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
