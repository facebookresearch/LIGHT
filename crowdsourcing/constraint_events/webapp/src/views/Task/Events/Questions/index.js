import React from "react";

import "./styles.css"

//COPY
import QuestionList from "./QuestionCopy";
//CUSTOM COMPONENENTS
import FormQuestion from "../../../../components/Questions/FormQuestion";
import BooleanQuestion from "../../../../components/Questions/BooleanQuestion"
import MultipleSelectQuestion from "../../../../components/Questions/MultipleSelectQuestion"
import FieldQuestion from "../../../../components/Questions/FieldQuestion"
import AttributeSetter from "../../../../components/AttributeSetter"

const Questions = ({object1, object2, interaction}) => {
    return (
       <>
            <FormQuestion
                question={QuestionList[1]}
                placeholder ="Description"
                formVal=""
            />
            <BooleanQuestion
                question={QuestionList[2]}
                trueAnswer={{name:"YES"} }
                falseAnswer={{name:"NO"} }
            >
                <MultipleSelectQuestion
                    question={QuestionList[0]}
                    answers={[object1.name, object2.name]}
                />
            </BooleanQuestion>
            <BooleanQuestion
                question={QuestionList[4]}
                trueAnswer={{name:"YES"} }
                falseAnswer={{name:"NO"} }
            >
                <FieldQuestion
                    question={""}
                    fields={[{name:"name", dropdown:false}, {name:"desc", dropdown:false}, {name:"location", dropdown:true, options:["in room", "held by actor", `in ${object1.name.toUpperCase()}`, `in ${object2.name.toUpperCase()}`]}]}
                />

            </BooleanQuestion>
            <BooleanQuestion
                question={QuestionList[3]}
                trueAnswer={{name:"YES"} }
                falseAnswer={{name:"NO"} }
            >
                <div style={{display:"flex", flexDirection:"row"}}>
                    <FormQuestion
                        question={object1.name}
                        upperCaseQuestion={true}
                        questionColor="blue"
                        placeholder ="Description"
                        formVal=""
                    />
                    <FormQuestion
                        question={object2.name}
                        upperCaseQuestion={true}
                        questionColor="orange"
                        placeholder ="Description"
                        formVal=""
                    />
                </div>
            </BooleanQuestion>
            <AttributeSetter objectName={object1.name} objectColor="blue" header=" Attributes" attributes={object1.attributes}/>
            <AttributeSetter objectName={object2.name} objectColor="orange" header=" Attributes" attributes={object2.attributes}/>
       </>
    );
}

export default Questions ;
