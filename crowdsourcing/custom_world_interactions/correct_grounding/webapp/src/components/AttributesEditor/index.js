//REACT
import React from "react";
//STYLING
import "./styles.css"
// Copy
import QuestionCopy from "../../TaskCopy.js";
//CUSTOM COMPONENTSimport QuestionOnSelect from "../../../../components/QuestionOnSelect";
import MultiFormQuestion from "../Questions/MultiFormQuestion";

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
    const splitWord = " <has property> "
    function handleUpdateBeforeAttributes(label, newAttribute) {
        let [obj, att] = label.split(splitWord)
        let newBeforeAttributes = {...beforeAttributes};
        newBeforeAttributes[obj][att] = newAttribute;
        setBeforeAttributes(newBeforeAttributes);
    }

    function handleUpdateAfterAttributes(label, newAttribute) {
        let [obj, att] = label.split(splitWord)
        let newAfterAttributes = {...afterAttributes};
        newAfterAttributes[obj][att] = newAttribute;
        setAfterAttributes(newAfterAttributes);
    }

    function reduceAttMap(attMap) {
        let newMap = {}
        for (let objName in attMap) {
            let attDict = attMap[objName];
            for (let attName in attDict) {
                newMap[objName + splitWord + attName] = attDict[attName];
            }
        }
        return newMap;
    }

    let beforeReduceMap = reduceAttMap(beforeAttributes);
    let afterReduceMap = reduceAttMap(afterAttributes);
    let beforeComplete = Object.entries(beforeReduceMap).filter(([n, x]) => n.indexOf('EXTRAS') == -1 && x.length == 0).length == 0;
    let afterComplete = Object.entries(afterReduceMap).filter(([n, x]) => n.indexOf('EXTRAS') == -1 && x.length == 0).length == 0;
    let beforePlaceholders = Object.entries(beforeReduceMap).map(([name, _]) => ((name.indexOf('EXTRAS') != -1) ? "Optional comma separated list of additional properties" : "'Required because ...' or 'Not required because ...'"))
    let afterPlaceholders = Object.entries(afterReduceMap).map(([name, _]) => ((name.indexOf('EXTRAS') != -1) ? "Optional comma separated list of additional properties" : "'Required because ...' or 'Not required because ...'"))

    /*------LIFECYCLE------*/
    //Upon object change sets descriptions for relevant object
    return (
        <div className="attributes-container">
            <div className="attributes-header">
                Attributes Questions
            </div>
            <div className="attributes-body">
                <MultiFormQuestion
                    question={QuestionList[0]}
                    entryMap={beforeReduceMap}
                    updateEntry={handleUpdateBeforeAttributes}
                    toolTipCopy={TipList[0].explanation}
                    hasToolTip={true}
                    isComplete={beforeComplete}
                    entryPlaceholder={beforePlaceholders}
                />
                <MultiFormQuestion
                    question={QuestionList[1]}
                    entryMap={afterReduceMap}
                    updateEntry={handleUpdateAfterAttributes}
                    toolTipCopy={TipList[1].explanation}
                    hasToolTip={true}
                    isComplete={afterComplete}
                    entryPlaceholder={afterPlaceholders}
                />
            </div>
        </div>
    );
}

export default AttributesEditor;
