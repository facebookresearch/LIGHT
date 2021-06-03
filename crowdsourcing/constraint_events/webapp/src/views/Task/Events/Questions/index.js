import React from "react";

import "./styles.css"

//COPY
import QuestionList from "./QuestionCopy";
//CUSTOM COMPONENENTS
import FormQuestion from "../../../../components/Questions/FormQuestion";


const Questions = () => {
    return (
       <>
            <FormQuestion
                question={QuestionList[1]}
                placeholder ="Description"
                formVal=""
            />
       </>
    );
}

export default Questions ;
