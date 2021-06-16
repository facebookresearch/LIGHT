import React from "react";

import "./styles.css"

//COPY
import QuestionCopy from "../../../../TaskCopy";
//CUSTOM COMPONENENTS
import FormQuestion from "../../../../components/Questions/FormQuestion";
import BooleanQuestion from "../../../../components/Questions/BooleanQuestion"
import MultipleSelectQuestion from "../../../../components/Questions/MultipleSelectQuestion"
import FieldQuestion from "../../../../components/Questions/FieldQuestion"
import AttributeSetter from "../../../../components/AttributeSetter"

const Questions = ({
    object1,
    object2,
    interaction,
    broadcastMessage,
    setBroadcastMessage,
    isCreatingEntity,
    setIsCreatingEntity,
    isRemovingObjects,
    setIsRemovingObjects,
    removedObjects,
    setRemovedObjects,
    isChangingDescription,
    setIsChangingDescription,
    primaryDescription,
    setPrimaryDescription,
    secondaryDescription,
    setSecondaryDescription,
    primaryModifiedAttributes,
    setPrimaryModifiedAttributes,
    secondaryModifiedAttributes,
    setSecondaryModifiedAttributes
}) => {
    const QuestionList = QuestionCopy.event.questions
    return (
       <>
            <FormQuestion
                question={QuestionList[1]}
                formVal={interaction}
                formFunction={setBroadcastMessage}
            />
            <BooleanQuestion
                question={QuestionList[2]}
                trueAnswer={{name:"YES"} }
                falseAnswer={{name:"NO"} }
                inverted={true}
            >

            </BooleanQuestion>
            <BooleanQuestion
                question={QuestionList[3]}
                trueAnswer={{name:"YES"} }
                falseAnswer={{name:"NO"} }
            >
                <MultipleSelectQuestion
                    question={QuestionList[a3]}
                    answers={[object1.name, object2.name]}
                />
            </BooleanQuestion>
            <BooleanQuestion
                question={QuestionList[4]}
                trueAnswer={{name:"YES"} }
                falseAnswer={{name:"NO"} }
            >
                <FieldQuestion

                    fields={[{name:"name", dropdown:false}, {name:"desc", dropdown:false}, {name:"location", dropdown:true, options:["in room", "held by actor", `in/on ${object1.name.toUpperCase()}`, `in/on ${object2.name.toUpperCase()}`]}]}
                />

            </BooleanQuestion>
            <BooleanQuestion
                question={QuestionList[5]}
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
            <AttributeSetter objectName={object1.name} objectColor="blue" header=" After this action:" attributes={object1.attributes} isConstraint={false}/>
            <AttributeSetter objectName={object2.name} objectColor="orange" header="  After this action:" attributes={object2.attributes} isConstraint={false}/>
       </>
    );
}

export default Questions ;
