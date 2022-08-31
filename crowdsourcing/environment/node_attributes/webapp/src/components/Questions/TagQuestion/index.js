/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

//REACT
import React, {useState, useEffect} from "react";
//STYLE
import "./styles.css";
//CUSTOM COMPONENTS
import TagRow from "./TagRow/index.js";

// TagQuestion - Container for typeahead boolean values
const TagQuestion = ({
    selection,// Objects who's attributes are being added and removed
    booleanAttributeOptions, // the default attributes for the selected object type
    updateFunction,// the function to update the attributes for the objects
})=>{



    return(
      <div className="tagquestion-body">
        {
          selection.length ?
          selection.map((item, index)=>{
            let {id, name, description, attributes}=item;
            let startingAttributes = attributes.map(attr=>{ //Generates array of attribute name strings that have a value of true
              if(attr.value){
              return(attr.name)
              }
            })
            return (
              <>
                <TagRow
                  key={index}
                  id={id}
                  name={name}
                  description={description}
                  startingAttributes={startingAttributes}
                  booleanAttributeOptions={booleanAttributeOptions}
                  updateFunction={(update)=>updateFunction(index, update)}
                />
              </>
            )
        })
        :
        null
      }
      </div>
    )
}
export default TagQuestion;
