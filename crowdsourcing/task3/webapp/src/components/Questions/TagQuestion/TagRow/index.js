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
import NumberForm from "../../../NumberForm"
//Copy
import TaskCopy from "../../../../TaskCopy";
const {numericAttributes} = TaskCopy

// SelectionList - A container for each selection item and their description
const TagRow = ({
    id,//attribute ID
    name,// attribute Name
    description,// attribute Description
    startingAttributes,//  Initial attributes selected in typeahead tokenizer
    booleanAttributes,//  Attributes that appear in tokenizer dropdown
    updateFunction, // function that updates payload data
    isNumericAttribute,
    startingNumericAttributeCount,
    numericUpdateFunction

})=>{
    //STATE
    const [attributes, setAttributes]=useState([])
    const [typeAheadTokens, setTypeAheadTokens] = useState([])
    const [selectedNumericAttributes, setSelectedNumericAttributes] = useState([]);
    //REFS
    const attributeRef = useRef();

    useEffect(()=>{
        let startingNumericAttributes = startingAttributes.filter(attr => (numericAttributes.indexOf(attr.name)>=0))
        setTypeAheadTokens(booleanAttributes)
        setAttributes(startingAttributes)
        selectedNumericAttributes(startingNumericAttributes)
    },[])

    useEffect(()=>{

    },[selectedNumericAttributes])

    useEffect(()=>{
        setAttributes(startingAttributes)
    },[startingAttributes])

    const changeHandler = ()=>{
        let {current} = attributeRef;
        let {state} =current;
        let {selected} = state;
        console.log("ON CHANGE!  ", selected)
        if(selected){
            let entries = selected
            let standardBooleanEntries = {}
            let customBooleanEntries = []
            if(!entries.length){
                setShowNumericAttributeForm(false)
            }
            entries.map((entry,index)=>{
                if(numericAttributes.indexOf(entry)>=0){
                    setShowNumericAttributeForm(true)
                }else if(typeof entry ==="string"){
                    setShowNumericAttributeForm(false)
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


    const renderTooltip = (props) => (
        <Tooltip id="button-tooltip" {...props}>
          {description}
        </Tooltip>
      );

    return(
        <>
            <div className="tagrow-container">
                <div className="tagrow-item__container">
                    <OverlayTrigger
                        placement="top"
                        delay={{ show: 250, hide: 400 }}
                        overlay={renderTooltip}
                    >
                        <p className="tagrow-item__text">{name}</p>
                    </OverlayTrigger>
                </div>
                <div style={{width:"70%"}}>
                <Typeahead
                    allowNew
                    defaultSelected={startingAttributes}
                    id="custom-selections-example"
                    multiple
                    newSelectionPrefix="Add a new item: "
                    options={booleanAttributes}
                    placeholder="Add Attributes here"
                    ref={attributeRef}
                    onChange={changeHandler}
                />
                </div>
            </div>
            {
                numericAttributes.length ?
                <NumberForm
                    key={name}
                    header={`${"limbs"} Count`}
                    formFunction={(updateValue)=>{
                    numericUpdateFunction(updateValue)
                    }}
                    startingVal={startingNumericAttributeCount}
                />
                :null
                }
        </>
    )
}
export default TagRow;
