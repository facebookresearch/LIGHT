//REACT
import React from "react";
//STYLING
import "./styles.css"
// Copy
import QuestionCopy from "../../TaskCopy.js";
//CUSTOM COMPONENTSimport QuestionOnSelect from "../../../../components/QuestionOnSelect";
import MultiFormQuestion from "../Questions/MultiFormQuestion";
import ListEditQuestion from "../Questions/ListEditQuestion";

// Attributes Editor Component - Container for Property Editing questions
const AttributesEditor = ({
    beforeAttributes,
    setBeforeAttributes,
    afterAttributes,
    setAfterAttributes,
}) => {
    // Assigning object attributes to variables for readability
    const QuestionList = QuestionCopy.attributes.questions
    const TipList = QuestionCopy.attributes.tutorialCopy;

    function handleUpdateBeforeAttributes(label, newAttribute) {
        let obj, att = label.split("|")
        let newBeforeAttributes = {...beforeAttributes};
        newBeforeAttributes[obj][att] = newAttribute;
        setBeforeAttributes(newBeforeAttributes);
    }

    function handleUpdateAfterAttributes(label, newAttribute) {
        let obj, att = label.split("|")
        let newAfterAttributes = {...afterAttributes};
        newAfterAttributes[obj][att] = newAttribute;
        setAfterAttributes(newAfterAttributes);
    }

    function reduceAttMap(attMap) {
        let newMap = {}
        for (objName in attMap) {
            let attDict = attMap[objName];
            for (attName in attDict) {
                newMap[objName + '|' + attName] = attDict[attName];
            }
        }
        return newMap;
    }

    let beforeReduceMap = reduceAttMap(beforeAttributes);
    let afterReduceMap = reduceAttMap(afterAttributes);


    /*------LIFECYCLE------*/
    //Upon object change sets descriptions for relevant object
    return (
        <div className="events-container">
            <div className="events-header">
                Narration Questions
            </div>
            <div className="events-body">
                <ListEditQuestion
                    question={QuestionList[0]}
                    entries={remainingObjects}
                    updateEntry={handleUpdateObjects}
                    toolTipCopy={TipList[0].explanation}
                    hasToolTip={true}
                    isComplete={remainingObjects.filter((x) => x.length == 0).length == 0}
                />
                <MultiFormQuestion
                    question={QuestionList[1]}
                    entryMap={beforeReduceMap}
                    updateEntry={handleUpdateBeforeAttributes}
                    toolTipCopy={TipList[1].explanation}
                    hasToolTip={true}
                    isComplete={Object.entries(beforeReduceMap).filter((n, x) => !n.indexOf('EXTRAS') && x.length == 0).length == 0}
                />
                <MultiFormQuestion
                    question={QuestionList[2]}
                    entryMap={afterReduceMap}
                    updateEntry={handleUpdateAfterAttributes}
                    toolTipCopy={TipList[2].explanation}
                    hasToolTip={true}
                    isComplete={Object.entries(afterReduceMap).filter((n, x) => !n.indexOf('EXTRAS') && x.length == 0).length == 0}
                />
            </div>
        </div>
    );
}

export default AttributesEditor;
