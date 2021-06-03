import React from "react";

import "./styles.css"

//COPY
import QuestionList from "./QuestionCopy";
//CUSTOM COMPONENENTS
import FormQuestion from "../../../../components/Questions/FormQuestion";
import BooleanQuestion from "../../../../components/Questions/BooleanQuestion"
import FieldQuestion from "../../../../components/Questions/FieldQuestion"


const Questions = () => {
    return (
       <>
            <FormQuestion
                question={QuestionList[1]}
                placeholder ="Description"
                formVal=""
            />
            <BooleanQuestion
                question={QuestionList[2]}
                trueAnswer="YES"
                falseAnswer="NO"
            >


            </BooleanQuestion>
       </>
    );
}

export default Questions ;
