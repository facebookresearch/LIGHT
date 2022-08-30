
/*****
 * Copyright (c) Meta Platforms, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

//REACT
// import React, { useEffect } from "react";
import React, { useEffect, useState } from "react";
//STYLE
import "./styles.css"
//COPY
import QuestionCopy from "../../../../TaskCopy.js";
//CUSTOM COMPONENTS
import QuestionOnSelect from "../../../../components/QuestionOnSelect";
import FormQuestion from "../../../../components/Questions/FormQuestion";
import InfoToolTip from "../../../../components/InfoToolTip";
import Checkbox from "../../../../components/Checkbox";
import BooleanQuestion from "../../../../components/Questions/BooleanQuestion";
import MultipleSelectQuestion from "../../../../components/Questions/MultipleSelectQuestion";
import FieldQuestion from "../../../../components/Questions/FieldQuestion";
import Highlightable from "highlightable";
import AttributeSetter from "../../../../components/AttributeSetter";

// Questions Component - Contains all of the forms relevant to the Events Questions and passes relevant state and setState functions to corresponding questions
const Questions = ({
    object1,
    object2,
    interaction,
    //Payload state and corresponding setState functions
    broadcastMessage,
    setBroadcastMessage,
    ranges,
    setRanges,
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
    setSecondaryModifiedAttributes
}) => {
    // Assigning object attributes to variables for readability
    let obj1Attr = object1.attributes
    let obj2Attr = object2.attributes
    const QuestionList = QuestionCopy.event.questions
    const TipList = QuestionCopy.event.tutorialCopy;
    let [selectedHighlighter, setSelectedHighlighter] = useState([]);
    /*------LIFECYCLE------*/
    //Upon object change sets descriptions for relevant object
    useEffect(() => {
        let obj1Desc = object1.desc;
        let obj2Desc = object2.desc;
        setPrimaryDescription(obj1Desc)
        setSecondaryDescription(obj2Desc)
    }, [object1, object2])

    useEffect(() => {
        setBroadcastMessage(interaction)
    }, [interaction])

    let getHighlightStyle = (({ highlighter }, charIndex) => {
        let style = highlighter === "ACTOR" ? {
            backgroundColor: '#CE93D8'
        } : highlighter === "OBJECT1" ? { backgroundColor: "#4FC3F7" } : highlighter === "OBJECT2" ? { backgroundColor: "#FFCC80" } : { backgroundColor: "#A5D6A7" };
        return style;
    });

    let updateRangesWithoutOverlaps = (range) => {
        if (selectedHighlighter.length > 0 && selectedHighlighter[0] !== "ERASER") {
            // currently highlighting something
            let { start: newStart, end: newEnd } = range;
            let rangesWithoutOverlaps = ranges.filter(({ start, end }) => start > newEnd || end < newStart);
            setRanges([...rangesWithoutOverlaps, { ...range, highlighter: selectedHighlighter[0] }]);
        } else {
            // Erase everything touching this highlight
            let { start: newStart, end: newEnd } = range;
            let rangesWithoutOverlaps = ranges.filter(({ start, end }) => start > newEnd || end < newStart);
            setRanges(rangesWithoutOverlaps);
        }
    }

    let updateBroadcastMessage = (broadcastMessage) => {
        setBroadcastMessage(broadcastMessage);
        setRanges([]);
    }

    return (
        <>
            <FormQuestion
                question={QuestionList[1]}
                formVal={interaction}
                // formFunction={setBroadcastMessage}
                formFunction={updateBroadcastMessage}
                toolTipCopy={TipList[0].explanation}
                hasToolTip={true}
                isComplete={(broadcastMessage.length && broadcastMessage !== interaction)}
            />
            <div className="form-container">
                <InfoToolTip
                    tutorialCopy={TipList[1].explanation}
                    hasToolTip={true}
                >
                    <div style={{ display: "flex", flexDirection: "row" }}>
                        <Checkbox isComplete={ranges.length >= 3} />
                        <h1 className="form-header" style={{ color: "black" }}>
                            {QuestionList[2]}
                        </h1>
                    </div>
                </InfoToolTip>

                <MultipleSelectQuestion
                    question={"SELECT THE CURRENT HIGHLIGHTER"}
                    answers={["ACTOR", "OBJECT1", "OBJECT2", "LOCATION", "ERASER"]}
                    colors={['#CE93D8', '#4FC3F7', '#FFCC80', '#A5D6A7']}
                    onlySelectOne={true}
                    selectFunction={setSelectedHighlighter}
                />

                <div className="highlightable-section">
                    <Highlightable ranges={ranges}
                        enabled={true}
                        onTextHighlighted={updateRangesWithoutOverlaps}
                        id={"uniqueId"}
                        onMouseOverHighlightedWord={(range) => { console.log('overlap with '); console.log(range); }}
                        highlightStyle={getHighlightStyle}
                        // text={'some text to highlight'}
                        text={broadcastMessage}
                    />
                </div>
            </div>

            <BooleanQuestion
                question={QuestionList[3]}
                trueAnswer={{ name: "YES" }}
                falseAnswer={{ name: "NO" }}
                formFunction={setIsRemovingObjects}
                toolTipCopy={TipList[1].explanation}
                hasToolTip={true}
                defaultOption={isRemovingObjects}
                isComplete={(isRemovingObjects !== null && (isRemovingObjects == false || (isRemovingObjects === true && removedObjects.length)))}
            >
                <MultipleSelectQuestion
                    question={QuestionList.a2}
                    answers={[object1.name, object2.name]}
                    selectFunction={setRemovedObjects}
                />
            </BooleanQuestion>
            <BooleanQuestion
                question={QuestionList[4]}
                trueAnswer={{ name: "YES" }}
                falseAnswer={{ name: "NO" }}
                formFunction={setIsChangingDescription}
                toolTipCopy={TipList[2].explanation}
                hasToolTip={true}
                isComplete={isChangingDescription !== null && (!isChangingDescription || (primaryDescription !== object1.desc || secondaryDescription !== object2.desc))}
                defaultOption={isChangingDescription}
            >
                <div style={{ display: "flex", flexDirection: "row", width: "100%" }}>
                    {!removedObjects.includes(object1.name) && <FormQuestion
                        question={object1.name}
                        upperCaseQuestion={true}
                        questionColor="blue"
                        placeholder="Description"
                        formVal={primaryDescription}
                        formFunction={setPrimaryDescription}
                        hasToolTip={false}
                    />}
                    {!removedObjects.includes(object2.name) && <FormQuestion
                        question={object2.name}
                        upperCaseQuestion={true}
                        questionColor="orange"
                        placeholder="Description"
                        formVal={secondaryDescription}
                        formFunction={setSecondaryDescription}
                        hasToolTip={false}
                    />}
                </div>
            </BooleanQuestion>
            <BooleanQuestion
                question={QuestionList[5]}
                trueAnswer={{ name: "YES" }}
                falseAnswer={{ name: "NO" }}
                formFunction={setIsCreatingEntity}
                toolTipCopy={TipList[3].explanation}
                hasToolTip={true}
                isComplete={(isCreatingEntity !== null && (isCreatingEntity == false || (isCreatingEntity === true && (createdEntity.name && createdEntity.desc && createdEntity.location))))}
            >
                <FieldQuestion

                    fields={[
                        { name: "name", dropdown: false },
                        { name: "desc", dropdown: false },
                        {
                            name: "location", dropdown: true,
                            options: [
                                { name: "in room", val: "in_room" },
                                { name: "held by actor", val: "in_actor" },
                                { name: `in/on ${object1.name.toUpperCase()}`, val: "in_used_item" },
                                { name: `in/on ${object2.name.toUpperCase()}`, val: "in_used_target_item" }
                            ]
                        }
                    ]}
                    formFunction={setCreatedEntity}
                    formState={createdEntity}
                />

            </BooleanQuestion>
            <QuestionOnSelect
                question={QuestionList[6]}
                secondaryQuestion={QuestionList.a6}
                answers={[
                    {
                        name: object1.name.toUpperCase(),
                        disabled: removedObjects.includes(object1.name),
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
                        disabled: removedObjects.includes(object2.name),
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
                isComplete={((!primaryIsChangingLocation && !secondaryIsChangingLocation) || (primaryIsChangingLocation && primaryNewLocation) || (secondaryIsChangingLocation && secondaryNewLocation))}
            />
        </>
    );
}

export default Questions;
