//REACT
import React, {useEffect} from "react";
//STYLE
import "./styles.css"
//COPY
import QuestionCopy from "../../../../TaskCopy.js";
//CUSTOM COMPONENENTS
import FormQuestion from "../../../../components/Questions/FormQuestion";
import BooleanQuestion from "../../../../components/Questions/BooleanQuestion";
import MultipleSelectQuestion from "../../../../components/Questions/MultipleSelectQuestion";
import FieldQuestion from "../../../../components/Questions/FieldQuestion";
import AttributeSetter from "../../../../components/AttributeSetter";

const Questions = ({
    object1,
    object2,
    interaction,
    broadcastMessage,
    setBroadcastMessage,
    isCreatingEntity,
    setIsCreatingEntity,
    createdEntity,
    setCreatedEntity,
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
    let obj1Attr = object1.attributes
    let obj2Attr = object2.attributes
    useEffect(()=>{
        let obj1Desc = object1.desc;
        let obj2Desc = object2.desc;
        setPrimaryDescription(obj1Desc)
        setSecondaryDescription(obj2Desc)
    },[object1, object2])
    const QuestionList = QuestionCopy.event.questions
    const TipList = QuestionCopy.event.tutorialCopy
    return (
       <>
            <FormQuestion
                question={QuestionList[1]}
                formVal={interaction}
                formFunction={setBroadcastMessage}
                toolTipCopy={TipList[0].explanation}
                hasToolTip={true}
                isComplete={(broadcastMessage.length && broadcastMessage!==interaction)}
            />
            <BooleanQuestion
                question={QuestionList[2]}
                trueAnswer={{name:"YES"} }
                falseAnswer={{name:"NO"} }
                formFunction={setIsRemovingObjects}
                toolTipCopy={TipList[1].explanation}
                hasToolTip={true}
                isComplete={(isRemovingObjects!==null && (isRemovingObjects==false || (isRemovingObjects===true && removedObjects.length)))}
            >
                <MultipleSelectQuestion
                    question={QuestionList.a2}
                    answers={[object1.name, object2.name]}
                    selectFunction={setRemovedObjects}
                />
            </BooleanQuestion>
            <BooleanQuestion
                question={QuestionList[3]}
                trueAnswer={{name:"YES"} }
                falseAnswer={{name:"NO"} }
                formFunction={setIsChangingDescription}
                toolTipCopy={TipList[2].explanation}
                hasToolTip={true}
                isComplete={isChangingDescription!==null}
            >
                <div style={{display:"flex", flexDirection:"row", width:"100%"}}>
                    <FormQuestion
                        question={object1.name}
                        upperCaseQuestion={true}
                        questionColor="blue"
                        placeholder ="Description"
                        formVal={primaryDescription}
                        formFunction={setPrimaryDescription}
                        hasToolTip={false}
                    />
                    <FormQuestion
                        question={object2.name}
                        upperCaseQuestion={true}
                        questionColor="orange"
                        placeholder ="Description"
                        formVal={secondaryDescription}
                        formFunction={setSecondaryDescription}
                        hasToolTip={false}
                    />
                </div>
            </BooleanQuestion>
            <BooleanQuestion
                question={QuestionList[4]}
                trueAnswer={{name:"YES"} }
                falseAnswer={{name:"NO"} }
                formFunction={setIsCreatingEntity}
                toolTipCopy={TipList[3].explanation}
                hasToolTip={true}
                isComplete={(isCreatingEntity!==null && (isCreatingEntity==false || (isCreatingEntity===true && (createdEntity.name && createdEntity.desc && createdEntity.location))))}
            >
                <FieldQuestion

                    fields={[
                        {name:"name", dropdown:false},
                        {name:"desc", dropdown:false},
                        {name:"location", dropdown:true,
                        options:[{name:"in room", val:"in_room"},
                        {name:"held by actor", val:"in_actor"},
                        {name:`in/on ${object1.name.toUpperCase()}`, val:"in_used_item"},
                        {name:`in/on ${object2.name.toUpperCase()}`, val:"in_used_target_item"}]}
                    ]}
                    formFunction={setCreatedEntity}
                    formState={createdEntity}
                />

            </BooleanQuestion>
            <AttributeSetter
                objectName={object1.name}
                objectColor="blue"
                header={QuestionList.setter}
                attributes={obj1Attr}
                isConstraint={false}
                setter={setPrimaryModifiedAttributes}
                toolTipCopy={TipList[4].explanation}
                hasToolTip={true}
            />
            <AttributeSetter
                objectName={object2.name}
                objectColor="orange"
                header={QuestionList.setter}
                attributes={obj2Attr}
                isConstraint={false}
                setter={setSecondaryModifiedAttributes}
                toolTipCopy={TipList[4].explanation}
                hasToolTip={true}
            />
       </>
    );
}

export default Questions ;
