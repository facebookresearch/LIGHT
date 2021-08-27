//REACT
import React, {useEffect, useState} from "react";
//STYLING
import "./styles.css";
//CUSTOM COMPONENTS
import MultipleSelectQuestion from "../Questions/MultipleSelectQuestion"
import DropdownSelect from "../DropdownSelect";
import FormatQuestion from "../Utils/FormatQuestion";
import InfoToolTip from "../InfoToolTip";
import Checkbox from "../Checkbox";


// Answers example [{name, secondaryQuestion:{type, question, answer(s)}}]
//QuestionOnSelect - Component that presents secondary question only when item is selected based on the selection
const QuestionOnSelect= ({
    question,//Multiple Select question
    secondaryQuestion,//Question prompted by selection
    answers, //Array of answers
    keywords,// keywords replacing any # in questions after formatting
    toolTipCopy,// Copy for desired tooltip
    hasToolTip,// Boolean stating whether or not this component has a tooltip
    isComplete,// Completion condition for question to be satisfactorily answered
})=>{
    /*------STATE------*/
    const [selectedAnswers, setSelectedAnswers] = useState([]);
    const [answerList, setAnswerList] = useState([])
    const [multipleSelectAnswers, setMultipleSelectAnswers] = useState([])
    /*------LIFECYCLE------*/
    useEffect(()=>{
        setAnswerList(answers)
        let updatedAnswers = answers.map(ans=>ans.name)
        setMultipleSelectAnswers(updatedAnswers)
    }, [answers])
    /*------HANDLERS------*/
    const selectHandler = (updatedAnswers)=>{
        answerList.map((ans,index)=>{
            const {name, onSelectFunction} = ans;
            if(updatedAnswers.indexOf(name)>=0){
                onSelectFunction(true)
            }else{
                onSelectFunction(false)
            }
        })
        setSelectedAnswers(updatedAnswers)
    }
    /*------UTILS------*/
    const secondaryQuestionSwitch = (answerObject)=>{
        const {secondaryQuestion } = answerObject;
        const {answers, question, secondaryOnSelectFunction, type}= secondaryQuestion;
        switch (type) {
            case "dropdown":
                let selectFunction = (update)=>{
                    secondaryOnSelectFunction(update)
                }
                return (
                    <div style={{width:"40%"}}>
                        <DropdownSelect
                            options={answers}
                            selectFunction={selectFunction}
                        />
                    </div>
                )
            default:
              return null
        }
    }

    return(
        <div>
            <InfoToolTip
                tutorialCopy={toolTipCopy}
                hasToolTip={hasToolTip}
            >
                <div style={{display:"flex", flexDirection:"row"}}>
                    {hasToolTip?<Checkbox isComplete={isComplete} />:null}
                    <FormatQuestion
                        question={question}
                        keywords={keywords}
                        containerStyle="booleanquestion-text"
                    />
                </div>
            </InfoToolTip>
            <MultipleSelectQuestion
                question={""}
                answers={multipleSelectAnswers}
                selectFunction={selectHandler}
            />
            <div className="select-question__container">
                {selectedAnswers.length ? <p className="select-question__header">{secondaryQuestion}</p> : null}
            </div>
            <div className="secondaryquestion-container" >
            {
                selectedAnswers.length
                ?
                answerList.map((ans, index)=>{
                    const {name, questionColor} = ans;
                    if(selectedAnswers.indexOf(name)>=0){
                        let secondQuestion = secondaryQuestionSwitch(ans)
                        return (
                            <div key={index}>
                                <p className="select-dropdown__header" style={{color:questionColor}}>{name}</p>
                                {secondQuestion}
                            </div>
                        )
                    }else{
                        return <div key={index} style={{width:"40%"}}/>
                    }
                })
                :
                null
            }
            </div>
        </div>
    )
}
export default QuestionOnSelect;
