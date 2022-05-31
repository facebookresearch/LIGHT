//REACT
import React, {useEffect} from "react";
//STYLE
import "./styles.css"
//COPY
import QuestionCopy from "../../../../TaskCopy.js";
//CUSTOM COMPONENTS
import QuestionOnSelect from "../../../../components/QuestionOnSelect";
import FormQuestion from "../../../../components/Questions/FormQuestion";
import BooleanQuestion from "../../../../components/Questions/BooleanQuestion";
import MultipleSelectQuestion from "../../../../components/Questions/MultipleSelectQuestion";
import FieldQuestion from "../../../../components/Questions/FieldQuestion";
import AttributeSetter from "../../../../components/AttributeSetter";

// Questions Component - Contains all of the forms relevant to the Events Questions and passes relevant state and setState functions to corresponding questions
const Questions = ({
    object1,
    object2,
    interaction,
    //Payload state and corresponding setState functions
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
    primaryIsChangingLocation,
    setPrimaryIsChangingLocation,
    primaryNewLocation,
    setPrimaryNewLocation,
    secondaryIsChangingLocation,
    setSecondaryIsChangingLocation,
    secondaryNewLocation,
    setSecondaryNewLocation,
    primaryModifiedAttributes,
    setPrimaryModifiedAttributes,
    secondaryModifiedAttributes,
    setSecondaryModifiedAttributes,
    createdModifiedAttributes,
    setCreatedModifiedAttributes
}) => {
    // Assigning object attributes to variables for readability
    let obj1Attr = object1.attributes
    let obj2Attr = object2.attributes
    const QuestionList = QuestionCopy.event.questions
    const TipList = QuestionCopy.event.tutorialCopy
    /*------LIFECYCLE------*/
    //Upon object change sets descriptions for relevant object
    useEffect(()=>{
        let obj1Desc = object1.desc;
        let obj2Desc = object2.desc;
        setPrimaryDescription(obj1Desc)
        setSecondaryDescription(obj2Desc)
    },[object1, object2])

    // useEffect(()=>{
    //     setBroadcastMessage(interaction)
    //    },[interaction])

    return (
       <>
            <FormQuestion
                question={QuestionList[1]}
                formVal={broadcastMessage}
                formFunction={()=>{}}
                formFunction={setBroadcastMessage}
                toolTipCopy={TipList[0].explanation}
                hasToolTip={true}
                isComplete={true}
                disabled={true}
            />
            <BooleanQuestion
                question={QuestionList[2]}
                trueAnswer={{name:"YES"} }
                falseAnswer={{name:"NO"} }
                formFunction={()=>{}}
                toolTipCopy={TipList[1].explanation}
                hasToolTip={true}
                defaultOption={isRemovingObjects}
                isComplete={true}
                disabled={true}
            >
                <MultipleSelectQuestion
                    question={QuestionList.a2}
                    answers={[object1.name, object2.name]}
                    // selectFunction={setRemovedObjects}
                    selectFunction={()=>{}}
                    disabled={true}
                    curSelectedAnswers={removedObjects}
                />
            </BooleanQuestion>
            <BooleanQuestion
                question={QuestionList[3]}
                trueAnswer={{name:"YES"} }
                falseAnswer={{name:"NO"} }
                formFunction={()=>{}}
                toolTipCopy={TipList[2].explanation}
                hasToolTip={true}
                isComplete={true}
                defaultOption={isChangingDescription}
                disabled={true}
            >
                <div style={{display:"flex", flexDirection:"row", width:"100%"}}>
                {!removedObjects.includes(object1.name) && <FormQuestion
                        question={object1.name}
                        upperCaseQuestion={true}
                        questionColor="blue"
                        placeholder="Description"
                        formVal={primaryDescription}
                        hasToolTip={false}
                        disabled={true}
                    />}
                    {!removedObjects.includes(object2.name) && <FormQuestion
                        question={object2.name}
                        upperCaseQuestion={true}
                        questionColor="orange"
                        placeholder="Description"
                        formVal={secondaryDescription}
                        hasToolTip={false}
                        disabled={true}
                    />}
                </div>
            </BooleanQuestion>
            <BooleanQuestion
                question={QuestionList[4]}
                trueAnswer={{name:"YES"} }
                falseAnswer={{name:"NO"} }
                formFunction={()=>{}}
                toolTipCopy={TipList[3].explanation}
                hasToolTip={true}
                isComplete={true}
                disabled={true}
                defaultOption={isCreatingEntity}
            >
                <FieldQuestion

                    fields={[
                        {name:"name", dropdown:false, value:isCreatingEntity ? createdEntity.name : null},
                        {name:"desc", dropdown:false, value:isCreatingEntity ? createdEntity.desc : null},
                        {name:"location", dropdown:true, value:isCreatingEntity ? createdEntity.location : null,
                            options:[
                                {name:"in room", val:"in_room"},
                                {name:"held by actor", val:"in_actor"},
                                {name:`in/on ${object1.name.toUpperCase()}`, val:"in_used_item"},
                                {name:`in/on ${object2.name.toUpperCase()}`, val:"in_used_target_item"}
                            ]
                        }
                    ]}
                    formFunction={()=>{}}
                    formState={createdEntity}
                    disabled={true}
                />

            </BooleanQuestion>
            <QuestionOnSelect
                question={QuestionList[5]}
                secondaryQuestion={QuestionList.a5}
                answers={[
                    {
                        name: object1.name.toUpperCase(),
                        disabled:removedObjects.includes(object1.name),
                        questionColor: "blue",
                        onSelectFunction: (status) => setPrimaryIsChangingLocation(status),
                        secondaryQuestion: {
                            type: "dropdown",
                            question: object1.name,
                            secondaryOnSelectFunction: (update) => setPrimaryNewLocation(update),
                            answers: [
                                { name: "in room", val: "in_room" },
                                { name: "held by actor", val: "in_actor" },
                                { name: `in/on ${object2.name.toUpperCase()}`, val: "in_used_target_item" },
                            ]
                        }
                    },
                    {
                        name: object2.name.toUpperCase(),
                        disabled:removedObjects.includes(object2.name),
                        questionColor: "orange",
                        onSelectFunction: (status) => setSecondaryIsChangingLocation(status),
                        secondaryQuestion: {
                            type: "dropdown",
                            question: object2.name,
                            secondaryOnSelectFunction: (update) => setSecondaryNewLocation(update),
                            answers: [
                                { name: "in room", val: "in_room" },
                                { name: "held by actor", val: "in_actor" },
                                { name: `in/on ${object1.name.toUpperCase()}`, val: "in_used_item" },
                            ]
                        }
                    }
                ].filter(({ disabled }) => !disabled)}
                toolTipCopy={TipList[4].explanation}
                hasToolTip={true}
                disabled={true}
                isComplete={true}
            />
            <AttributeSetter
                objectName={object1.name}
                objectColor="blue"
                header={QuestionList.setter}
                attributes={obj1Attr}
                isConstraint={false}
                setter={setPrimaryModifiedAttributes}
                toolTipCopy={TipList[5].explanation}
                hasToolTip={true}
                defaultAttributes={primaryModifiedAttributes}
            />
            <AttributeSetter
                objectName={object2.name}
                objectColor="orange"
                header={QuestionList.setter}
                attributes={obj2Attr}
                isConstraint={false}
                setter={setSecondaryModifiedAttributes}
                toolTipCopy={TipList[5].explanation}
                hasToolTip={true}
                defaultAttributes={secondaryModifiedAttributes}
            />
            {isCreatingEntity ? <AttributeSetter
                objectName={createdEntity.name}
                objectColor="green"
                header={QuestionList.setter}
                attributes={obj2Attr}
                isConstraint={false}
                setter={setCreatedModifiedAttributes}
                toolTipCopy={TipList[5].explanation}
                defaultAttributes={createdModifiedAttributes}
                hasToolTip={true}
            /> : <div />}
       </>
    );
}

export default Questions ;
