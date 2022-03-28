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
    //Payload state and corresponding setState functions
    isSecondaryHeld,
    setIsSecondaryHeld,
    isReversible,
    setIsReversible,
    isLocationConstrained,
    setIsLocationConstrained,
    constraintLocation,
    setConstraintLocation,
    primaryConstrainingAttributes,
    setPrimaryConstrainingAttributes,
    secondaryConstrainingAttributes,
    setSecondaryConstrainingAttributes,
    isCreatingEntity,
    createdEntity,
    isInfinite,
    setIsInfinite,
    timesRemaining,
    setTimesRemaining,
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
            defaultAttributes={primaryConstrainingAttributes}
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
            defaultAttributes={secondaryConstrainingAttributes}
        />
        <BooleanQuestion
            question={QuestionList[1]}
            keywords={[{color:"orange", item:objName2}]}
            trueAnswer={{name:"YES"} }
            falseAnswer={{name:"NO"} }
            formFunction={setIsSecondaryHeld}
            toolTipCopy={TipList[0].explanation}
            hasToolTip={true}
            isComplete={isSecondaryHeld!==null}
        />
        <BooleanQuestion
            question={QuestionList[2]}
            keywords={[{color:"orange", item:objName2}, {color:"blue", item:objName1}]}
            trueAnswer={{name:"YES"} }
            falseAnswer={{name:"NO"} }
            formFunction={setIsReversible}
            toolTipCopy={TipList[1].explanation}
            hasToolTip={true}
            isComplete={isReversible!==null}
        />
        <BooleanQuestion
            question={QuestionList[3]}
            trueAnswer={{name:"YES"} }
            falseAnswer={{name:"NO"} }
            formFunction={setIsInfinite}
            inverted={true}
            toolTipCopy={TipList[2].explanation}
            hasToolTip={true}
            isComplete={isInfinite!==null}
        >
            <NumberQuestion
                question={QuestionList[4]}
                formFunction={setTimesRemaining}
            />
        </BooleanQuestion>

        <BooleanQuestion
            question={QuestionList[5]}
            trueAnswer={{name:"YES"} }
            falseAnswer={{name:"NO"} }
            formFunction={setIsLocationConstrained}
            toolTipCopy={TipList[3].explanation}
            hasToolTip={true}
            isComplete={isLocationConstrained!==null && (isLocationConstrained==false || (isLocationConstrained==true && constraintLocation.length))}
        >
            <FormQuestion
                question={QuestionList[6]}
                placeholder ="Description"
                formVal={constraintLocation}
                formFunction={setConstraintLocation}
                disabled={false}
            />
        </BooleanQuestion>
   </>
    );
}

export default Questions ;
