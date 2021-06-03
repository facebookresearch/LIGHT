import React from "react";

import "./styles.css"

//COPY
import QuestionList from "./QuestionCopy";
//CUSTOM COMPONENENTS
import FormQuestion from "../../../../components/Questions/FormQuestion";
import BooleanQuestion from "../../../../components/Questions/BooleanQuestion"
import FieldQuestion from "../../../../components/Questions/FieldQuestion"
import AttributeSetter from "../../../../components/AttributeSetter"

const Questions = () => {
    return (
       <>
            <AttributeSetter />
            <BooleanQuestion
                question={QuestionList[2]}
                trueAnswer="YES"
                falseAnswer="NO"
            />
            <BooleanQuestion
                question={QuestionList[3]}
                trueAnswer="YES"
                falseAnswer="NO"
            />

            <BooleanQuestion
                question={QuestionList[4]}
                trueAnswer="YES"
                falseAnswer="NO"
            >
            </BooleanQuestion>
            <AttributeSetter />
       </>
    );
}

export default Questions ;
