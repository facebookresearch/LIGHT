//REACT
import React, {useState, useEffect} from "react";
//STYLES
import "./styles"
//BOOTSTRAP
import OverlayTrigger from 'react-bootstrap/OverlayTrigger';
import Tooltip from 'react-bootstrap/Tooltip';
//TYPEAHEAD TOKENIZER
import { Typeahead } from 'react-bootstrap-typeahead';


// SelectionList - A container for each selection item and their description
const TagRow = ({
    name,
    description,
    booleanAttributes
})=>{
    const [attributes, setAttributes]=useState([])
    useEffect(()=>{
        setAttributes(booleanAttributes)
    },[])


    const renderTooltip = (props) => (
        <Tooltip id="button-tooltip" {...props}>
          {description}
        </Tooltip>
      );


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
            <Typeahead
              allowNew
              id="custom-selections-example"
              multiple
              newSelectionPrefix="Add a new item: "
              options={attributes}
              placeholder="Type anything..."
            />

        </div>
    )
}
export default TagRow;
