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
                <FieldQuestion
                    question={QuestionList[3]}
                    fields={["name", "desc", "location"]}
                />

            </BooleanQuestion>
            <BooleanQuestion
                question={QuestionList[4]}
                trueAnswer="YES"
                falseAnswer="NO"
            >
                <div >
                    <FormQuestion
                        question="OBJECT 1"
                        placeholder ="Description"
                        formVal=""
                    />
                    <FormQuestion
                        question="OBJECT 1"
                        placeholder ="Description"
                        formVal=""
                    />
                </div>
            </BooleanQuestion>
            <AttributeSetter />
       </>
    );
}

export default Questions ;
