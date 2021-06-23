//REACT
import React from "react";
//STYLING
import "./styles.css"
//COPY
import QuestionList from "./QuestionCopy";
//CUSTOM COMPONENENTS
import FormQuestion from "../../../../components/Questions/FormQuestion";
import BooleanQuestion from "../../../../components/Questions/BooleanQuestion";
import FieldQuestion from "../../../../components/Questions/FieldQuestion";
import AttributeSetter from "../../../../components/AttributeSetter";
import NumberQuestion from "../../../../components/Questions/NumberQuestion";

const Questions = ({
    object1,
    object2,
    interaction,
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

}) => {
    let obj1Attr = object1.attributes
    let obj2Attr = object2.attributes
    let objName1 = object1.name.toUpperCase();
    let objName2 = object2.name.toUpperCase();
    return (
       <>
            <AttributeSetter
                objectName={object1.name}
                objectColor="blue"
                header=" Constraints for interaction:"
                attributes={obj1Attr}
                isConstraint={true}
                setter={setPrimaryConstrainingAttributes}
            />
            <AttributeSetter
                objectName={object2.name}
                objectColor="orange"
                header=" Constraints for interaction:"
                attributes={obj2Attr}
                isConstraint={true}
                setter={setSecondaryConstrainingAttributes}
            />
            <BooleanQuestion
                question={"1.  Does # need to be held?"}
                keywords={[{color:"orange", item:objName2}]}
                trueAnswer={{name:"YES"} }
                falseAnswer={{name:"NO"} }
                formFunction={setIsSecondaryHeld}
            />
            <BooleanQuestion
                question={"2.  Could one use # with # and expect the same outcome?"}
                keywords={[{color:"orange", item:objName2}, {color:"blue", item:objName1}]}
                trueAnswer={{name:"YES"} }
                falseAnswer={{name:"NO"} }
                formFunction={setIsReversible}
            />

            <BooleanQuestion
                question={QuestionList[4]}
                trueAnswer={{name:"YES"} }
                falseAnswer={{name:"NO"} }
                formFunction={setIsLocationConstrained}
            >
                <FormQuestion
                    question="Where would that location be?"
                    placeholder ="Description"
                    formVal={constraintLocation}
                    formFunction={setConstraintLocation}
                />
            </BooleanQuestion>
       </>
    );
}

export default Questions ;
