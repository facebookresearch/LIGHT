//REACT
import React from "react";
//STYLING
import "./styles.css"
// Copy
import QuestionCopy from "../../TaskCopy.js";
//CUSTOM COMPONENTSimport QuestionOnSelect from "../../../../components/QuestionOnSelect";
import MultiFormQuestion from "../../components/Questions/MultiFormQuestion";
import ListEditQuestion from "../../components/Questions/ListEditQuestion";

// Objects Editor Component - Container for Object Editing questions
const ObjectsEditor = ({
    remainingObjects,
    setRemainingObjects,
    finalDescriptions,
    setFinalDescriptions,
    finalLocations,
    setFinalLocations,
    afterAttributes,
    setAfterAttributes,
}) => {
    // Assigning object attributes to variables for readability
    const QuestionList = QuestionCopy.objects.questions
    const TipList = QuestionCopy.objects.tutorialCopy;

    function handleUpdateObjects(value, idx, isRemove) {
        if (idx == null) {
            // create new entry case
            let newDescriptions = {...finalDescriptions, "": ""}
            let newLocations = {...finalLocations, "": ""}
            let newAfterAttributes = {...afterAttributes, "": {"EXTRAS": ""}}
            let newRemainingObjects = [...remainingObjects, ""]
            setRemainingObjects(newRemainingObjects);
            setFinalDescriptions(newDescriptions);
            setFinalLocations(newLocations);
            setAfterAttributes(newAfterAttributes);
        } else if (isRemove) {
            // remove entry case
            let entry = remainingObjects[idx];
            let newDescriptions = {...finalDescriptions};
            let newLocations = {...finalLocations};
            let newRemainingObjects = [...remainingObjects];
            let newAfterAttributes = {...afterAttributes}
            newRemainingObjects.splice(idx, 1);
            delete newDescriptions[entry.toLowerCase()];
            delete newLocations[entry.toLowerCase()];
            delete newAfterAttributes[entry.toLowerCase()];
            setRemainingObjects(newRemainingObjects);
            setFinalDescriptions(newDescriptions);
            setFinalLocations(newLocations);
            setAfterAttributes(newAfterAttributes);
        } else {
            // update value case
            let entry = remainingObjects[idx];
            let newDescriptions = {...finalDescriptions};
            let newLocations = {...finalLocations};
            let newRemainingObjects = [...remainingObjects];
            let newAfterAttributes = {...afterAttributes}
            newRemainingObjects[idx] = value;
            newDescriptions[value.toLowerCase()] = newDescriptions[entry.toLowerCase()];
            newLocations[value.toLowerCase()] = newLocations[entry.toLowerCase()];
            newAfterAttributes[value.toLowerCase()] = newAfterAttributes[entry.toLowerCase()];
            delete newDescriptions[entry.toLowerCase()];
            delete newLocations[entry.toLowerCase()];
            delete newAfterAttributes[entry.toLowerCase()];
            setRemainingObjects(newRemainingObjects);
            setFinalDescriptions(newDescriptions);
            setFinalLocations(newLocations);
            setAfterAttributes(newAfterAttributes);
        }
    }

    function handleUpdateDescription(label, newDesc) {
        let newDescriptions = {...finalDescriptions};
        newDescriptions[label] = newDesc;
        setFinalDescriptions(newDescriptions);
    }

    function handleUpdateLocation(label, newLoc) {
        let newLocations = {...finalLocations};
        newLocations[label] = newLoc;
        setFinalLocations(newLocations);
    }

    /*------LIFECYCLE------*/
    //Upon object change sets descriptions for relevant object
    return (
        <div className="objects-container">
            <div className="objects-header">
                Objects Questions
            </div>
            <div className="objects-body">
                <ListEditQuestion
                    question={QuestionList[0]}
                    entries={remainingObjects}
                    updateEntry={handleUpdateObjects}
                    toolTipCopy={TipList[0].explanation}
                    hasToolTip={true}
                    isComplete={remainingObjects.filter((x) => x.length == 0).length == 0}
                    entryPlaceholder={"Enter an item that remains after the interaction"}
                />
                <MultiFormQuestion
                    question={QuestionList[1]}
                    entryMap={finalDescriptions}
                    updateEntry={handleUpdateDescription}
                    toolTipCopy={TipList[1].explanation}
                    hasToolTip={true}
                    isComplete={Object.entries(finalDescriptions).filter(([_, x]) => x.length == 0).length == 0}
                    entryPlaceholder={
                        Object.entries(finalDescriptions).map(([name, _]) => "Final description for " + name)
                    }
                />
                <MultiFormQuestion
                    question={QuestionList[2]}
                    entryMap={finalLocations}
                    updateEntry={handleUpdateLocation}
                    toolTipCopy={TipList[2].explanation}
                    hasToolTip={true}
                    isComplete={Object.entries(finalLocations).filter(([_, x]) => x.length == 0).length == 0}
                    entryPlaceholder={
                        Object.entries(finalDescriptions).map(([name, _]) => "Final location for " + name)
                    }
                />
            </div>
        </div>
    );
}

export default ObjectsEditor;
