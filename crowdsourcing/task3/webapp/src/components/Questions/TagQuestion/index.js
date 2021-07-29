//REACT
import React, {useState, useEffect} from "react";
//STYLE
import "./styles.css";
//CUSTOM COMPONENTS
import TagRow from "./TagRow/index.js";


// TagQuestion - Container for typeahead boolean values
const TagQuestion = ({
    header,
    selection,
    booleanAttributes
})=>{



    return(
      <div className="tagquestion-container">
        <h3 className="tagquestion-header">
          ATTRIBUTES
        </h3>
        <div className="tagquestion-body">
          {
            selection.length ?
            selection.map((item, index)=>{
              let {name, description}=item
              return (
                <TagRow
                  key={index}
                  name={name}
                  description={description}
                  booleanAttributes={booleanAttributes}
                />
              )
          })
          :
          null
          }
        </div>
      </div>
    )
}
export default TagQuestion;
