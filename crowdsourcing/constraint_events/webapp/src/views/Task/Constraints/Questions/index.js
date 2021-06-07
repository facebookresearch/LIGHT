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
    return (
       <>
            <AttributeSetter objectName={object1.name} objectColor="blue" header=" Attribute Constraints" attributes={object1.attributes} />
            <AttributeSetter objectName={object2.name} objectColor="orange" header=" Attribute Constraints" attributes={object2.attributes} />
            <BooleanQuestion
                question={QuestionList[2]}
                trueAnswer={{name:"YES"} }
                falseAnswer={{name:"NO"} }
            />
            <BooleanQuestion
                question={`Could one use ${object2.name.toUpperCase()} with ${object1.name.toUpperCase()}  and expect the same outcome?`}
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
