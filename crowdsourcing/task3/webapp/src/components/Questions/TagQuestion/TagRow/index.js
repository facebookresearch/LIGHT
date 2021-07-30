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
    name,
    description,
    startingAttributes,
    booleanAttributes,
    attributeRef
})=>{
    const [attributes, setAttributes]=useState([])
    const [typeAheadTokens, setTypeAheadTokens] = useState([])
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

        console.log(attributes)
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
            />
            </div>
        </div>
    )
}
export default TagRow;
