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
       </>
    );
}

export default Questions ;
