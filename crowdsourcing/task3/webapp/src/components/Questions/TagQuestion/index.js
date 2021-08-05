//REACT
import React, {useState, useEffect} from "react";
//STYLE
import "./styles.css";
//CUSTOM COMPONENTS
import TagRow from "./TagRow/index.js";
import NumberForm from "../../NumberForm"
//Copy
import TaskCopy from "../../../TaskCopy";
const {numericAttributes} = TaskCopy

// TagQuestion - Container for typeahead boolean values
const TagQuestion = ({
    header,//Text at head of container
    selection,// Objects who's attributes are being added and removed
    booleanAttributes, // the default attributes for the selected object type
    updateFunction,// the function to update the attributes for the objects
    numericAttributeUpdateFunction// tthe function that updates numeric attribute values
})=>{



    return(
      <div className="tagquestion-container">
        <h3 className="tagquestion-header">
          {header}
        </h3>
        <div className="tagquestion-body">
          {
            selection.length ?
            selection.map((item, index)=>{
              let isNumericAttribute
              let {id, name, description, attributes}=item;
              let numericAttribute =attributes.filter(attr => (numericAttributes.indexOf(attr.name)>=0)) //filters for limb attribute in attributes array
              isNumericAttribute = !!numericAttribute.length// checks to see if numeric attribute is present
              let startingNumericAttributeCount = 0;
              if(isNumericAttribute){
                startingNumericAttributeCount = numericAttribute[0].value //Take limb count from value key of limb attribute
              }
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
                    booleanAttributes={booleanAttributes}
                    updateFunction={(update)=>updateFunction(index, update)}
                    isNumericAttribute={isNumericAttribute}
                    numericUpdateFunction={isNumericAttribute
                      ?
                      (updateValue)=>{
                        numericAttributeUpdateFunction(index, numericAttribute.name, updateValue)
                    }
                    :
                    ()=>{}
                    }
                    startingNumericAttributeCount={startingNumericAttributeCount}
                  />
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
