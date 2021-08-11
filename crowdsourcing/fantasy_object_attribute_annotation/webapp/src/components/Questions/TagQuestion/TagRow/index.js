//REACT
import React, {useState, useEffect, useRef} from "react";
//STYLES
import "./styles.css";
//BOOTSTRAP
import OverlayTrigger from 'react-bootstrap/OverlayTrigger';
import Tooltip from 'react-bootstrap/Tooltip';
//TYPEAHEAD TOKENIZER
import { Typeahead } from 'react-bootstrap-typeahead';
//CUSTOM COMPONENTS
import ToolTip from "../../../ToolTip";
//Copy
import TaskCopy from "../../../../TaskCopy";
const {numericAttributes} = TaskCopy

// SelectionList - A container for each selection item and their description
const TagRow = ({
    id,//attribute ID
    name,// attribute Name
    description,// attribute Description
    startingAttributes,//  Initial attributes selected in typeahead tokenizer
    booleanAttributeOptions,//  Attributes that appear in tokenizer dropdown
    updateFunction, // function that updates payload data

})=>{
    /*--------------------REFS--------------------*/
    const attributeRef = useRef();


    const changeHandler = ()=>{
        let {current} = attributeRef;
        let {state} =current;
        let {selected} = state;
        console.log("ON CHANGE!  ", selected)
        if(selected){
            let entries = selected
            let standardBooleanEntries = {}
            let customBooleanEntries = []
            entries.map((entry,index)=>{
                if(typeof entry ==="string"){
                    standardBooleanEntries[entry]=true;
                }else if(entry.label){
                    let {label} =entry;
                    customBooleanEntries = [...customBooleanEntries, label]
                }
            })
            let rowUpdate = {...standardBooleanEntries, custom: customBooleanEntries}
            updateFunction(rowUpdate)
        }
    }


    return(
        <>
            <div className="tagrow-container">
                <div className="tagrow-item__container">
                    <ToolTip
                        toolTipText={description}
                    >
                        <p className="tagrow-item__text">{name}</p>
                    </ToolTip>
                </div>
                <div style={{width:"70%"}}>
                <Typeahead
                    allowNew
                    defaultSelected={startingAttributes}
                    id="custom-selections-example"
                    multiple
                    newSelectionPrefix="Add a new attribute:  "
                    options={booleanAttributeOptions}
                    placeholder="Add Attributes here"
                    ref={attributeRef}
                    onChange={changeHandler}
                />
                </div>
            </div>
        </>
    )
}
export default TagRow;
