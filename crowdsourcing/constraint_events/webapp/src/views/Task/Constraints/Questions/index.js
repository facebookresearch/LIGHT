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
            <AttributeSetter object1={object1} object1={object2}/>
            <BooleanQuestion
                question={QuestionList[2]}
                trueAnswer={{name:"YES"} }
                falseAnswer={{name:"NO"} }
            />
            <BooleanQuestion
                question={QuestionList[3]}
                trueAnswer={{name:"YES"} }
                falseAnswer={{name:"NO"} }
            />

            <BooleanQuestion
                question={QuestionList[4]}
                trueAnswer={{name:"YES"} }
                falseAnswer={{name:"NO"} }
            >
            </BooleanQuestion>
            <AttributeSetter object1={object1} object1={object2} />
       </>
    );
}

export default Questions ;
