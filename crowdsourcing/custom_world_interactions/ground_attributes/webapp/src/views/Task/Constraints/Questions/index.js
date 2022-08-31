/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

//REACT
import React from "react";
//STYLING
import "./styles.css"
//COPY
import QuestionCopy from "../../../../TaskCopy.js";
//CUSTOM COMPONENENTS
import FormQuestion from "../../../../components/Questions/FormQuestion";
import BooleanQuestion from "../../../../components/Questions/BooleanQuestion";
import AttributeSetter from "../../../../components/AttributeSetter";
import NumberQuestion from "../../../../components/Questions/NumberQuestion";

// Questions Component - Contains all of the forms relevant to the Constraint Questions and passes relevant state and setState functions to corresponding questions
const Questions = ({
    object1,
    object2,
    interaction,
    //Payload state and corresponding setState function
    primaryConstrainingAttributes,
    setPrimaryConstrainingAttributes,
    secondaryConstrainingAttributes,
    setSecondaryConstrainingAttributes,
    isCreatingEntity,
    createdEntity,
    hasBackstory,
    setHasBackstory
}) => {
    // Assigning object attributes to variables for readability
    let obj1Attr = object1.attributes
    let obj2Attr = object2.attributes
    let objName1 = object1.name.toUpperCase();
    let objName2 = object2.name.toUpperCase();
    const QuestionList = QuestionCopy.constraint.questions
    const TipList = QuestionCopy.constraint.tutorialCopy
    return (
       <>
            <AttributeSetter
                objectName={object1.name}
                objectColor="blue"
                header={QuestionList[0]}
                attributes={obj1Attr}
                isConstraint={true}
                setter={setPrimaryConstrainingAttributes}
                toolTipCopy={TipList[0].explanation}
                hasToolTip={true}
            />
            <AttributeSetter
                objectName={object2.name}
                objectColor="orange"
                header={QuestionList[0]}
                attributes={obj2Attr}
                isConstraint={true}
                setter={setSecondaryConstrainingAttributes}
                toolTipCopy={TipList[0].explanation}
                hasToolTip={true}
            />
            {/* <BooleanQuestion
                question={QuestionList[1]}
                keywords={[{color:"orange", item:objName2}]}
                trueAnswer={{name:"YES"} }
                falseAnswer={{name:"NO"} }
                formFunction={setHasBackstory}
                toolTipCopy={TipList[1].explanation}
                hasToolTip={true}
                isComplete={hasBackstory!==null}
            /> */}
       </>
    );
}

export default Questions ;
