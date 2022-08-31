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
import AttributeQuestionRow from "./AttributeQuestionRow";


// AttributeQuestions - Renders all default questions for a item type
const AttributeQuestions = ({
    selection,// Objects who's attributes are being added and removed
    defaultQuestions,
    updateFunction// the function to update the attributes for the objects
})=>{



    return(
        <div className="attributequestion-body" >
                {
                    selection.length ?
                    selection.map((node, index)=>{
                        return (
                            <AttributeQuestionRow
                                key={index}
                                selection={node}
                                defaultQuestions={defaultQuestions}
                                updateFunction={(updateKey, updateValue)=>updateFunction(index, updateKey, updateValue)}
                            />
                        )
                    })
                    :
                    null
                }
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
