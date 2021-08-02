//REACT
import React, {useState, useEffect, useRef} from "react";
//STYLES
import "./styles.css";
//BOOTSTRAP
import OverlayTrigger from 'react-bootstrap/OverlayTrigger';
import Tooltip from 'react-bootstrap/Tooltip';
//TYPEAHEAD TOKENIZER
import { Typeahead } from 'react-bootstrap-typeahead';


// SelectionList - A container for each selection item and their description
const TagRow = ({
    id,
    name,
    description,
    startingAttributes,
    booleanAttributes,
    updateFunction
})=>{
    //STATE
    const [attributes, setAttributes]=useState([])
    const [typeAheadTokens, setTypeAheadTokens] = useState([])
    //REFS
    const attributeRef = useRef();

    useEffect(()=>{
        setTypeAheadTokens(booleanAttributes)
        setAttributes(startingAttributes)
    },[])

    useEffect(()=>{
        console.log("ATT UPDATE", attributes)
        setAttributes(startingAttributes)
    },[startingAttributes])


    const renderTooltip = (props) => (
        <Tooltip id="button-tooltip" {...props}>
          {description}
        </Tooltip>
      );
    const changeHandler = ()=>{
        let {current} = attributeRef;
        let {state} =current;
        let {selected} = state;
        if(selected){
            let entries = selected
            let standardBooleanEntries = {}
            let customBooleanEntries = []
            entries.map((entry,index)=>{
                if(typeof entry ==="string"){
                    standardBooleanEntries[entry]=true
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
    )
}
export default TagRow;
