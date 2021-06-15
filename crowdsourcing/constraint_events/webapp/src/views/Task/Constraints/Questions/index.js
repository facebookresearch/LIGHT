import React from "react";

import "./styles.css"

//COPY
import QuestionList from "./QuestionCopy";
//CUSTOM COMPONENENTS
import FormQuestion from "../../../../components/Questions/FormQuestion";
import BooleanQuestion from "../../../../components/Questions/BooleanQuestion"
import FieldQuestion from "../../../../components/Questions/FieldQuestion"
import AttributeSetter from "../../../../components/AttributeSetter"

const Questions = ({object1, object2, interaction}) => {
    let objName1 = object1.name.toUpperCase();
    let objName2 = object2.name.toUpperCase()
    return (
       <>
            <AttributeSetter objectName={object1.name} objectColor="blue" header=" Constraints for interaction:" attributes={[]} isConstraint={true} />
            <AttributeSetter objectName={object2.name} objectColor="orange" header=" Constraints for interaction:" attributes={[]} isConstraint={true} />
            <BooleanQuestion
                question={"Does # need to be held?"}
                keywords={[{color:"orange", item:objName2}]}
                trueAnswer={{name:"YES"} }
                falseAnswer={{name:"NO"} }
            />
            <BooleanQuestion
                question={"Could one use # with # and expect the same outcome?"}
                keywords={[{color:"orange", item:objName2}, {color:"blue", item:objName1}]}
                trueAnswer={{name:"YES"} }
                falseAnswer={{name:"NO"} }
            />

            <BooleanQuestion
                question={QuestionList[4]}
                trueAnswer={{name:"YES"} }
                falseAnswer={{name:"NO"} }
            >
                <FormQuestion
                    question="Where would that location be?"
                    placeholder ="Description"
                    formVal=""
                />
            </BooleanQuestion>
       </>
    );
}

export default Questions ;
