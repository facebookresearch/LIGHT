//REACT
import React, {useState, useEffect} from "react";
//STYLE
import "./styles.css";
//CUSTOM COMPONENTS
import MultipleSelectQuestion from "../../../components/Questions/MultipleSelectQuestion";
import MultipleChoiceQuestion from "../../../components/Questions/MultipleChoiceQuestion";
import NumberForm from "../../../components/NumberForm"


// AttributeQuestions - Renders all default questions for a item type
const AttributeQuestions = ({
    header,//Text at head of container
    selection,// Objects who's attributes are being added and removed
    booleanAttributes, // the default attributes for the selected object type
    updateFunction,// the function to update the attributes for the objects
    numericAttributeUpdateFunction,// tthe function that updates numeric attribute values
    children
})=>{



    return(
        <div>
            <div>
                {children}
            </div>
        </div>
    )
}
export default AttributeQuestions;

/*
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
*/
