//REACT
import React, {useState, useEffect} from "react";
//STYLE
import "./styles.css";
//CUSTOM COMPONENTS
import TagRow from "./TagRow/index.js";
import NumberForm from "../../NumberForm"


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
              let {name, description, attributes}=item;
              let limbAttr =attributes.filter(attr => (attr.name=="limbs")) //filters for limb attribute in attributes array
              let hasLimbs = limbAttr.length// checks to see if limb attribute is present
              let startingLimbCount =0
              if(hasLimbs){
                startingLimbCount = limbAttr[0].value //Take limb count from value key of limb attribute
              }
              return (
                <>
                  <TagRow
                    key={index}
                    name={name}
                    description={description}
                    booleanAttributes={booleanAttributes}
                  />
                  {
                    hasLimbs ?
                    <NumberForm
                      key={name}
                      header="Limb Count"
                      formFunction={()=>{}}
                      startingVal={startingLimbCount}
                    />
                    :null
                  }
                </>
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
