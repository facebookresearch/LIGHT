//REACT
import React, {useState, useEffect} from "react";
//STYLE
import "./styles.css";
//CUSTOM COMPONENTS
import TagRow from "./TagRow";


// TagQuestion - Container for typeahead boolean values
const TagQuestion = ({
    selection,
    booleanAttributes
})=>{


    return(
      <div className="tagquestion-container">
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
    )
}
export default TagQuestion;
