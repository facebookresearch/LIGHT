/* REACT */
import react, {useState, useEffect} from "react";

/* STYLES */
import "./styles.css";
/* BOOTSTRAP COMPONENTS */
import Form from 'react-bootstrap/form';
/* CUSTOM COMPONENTS */
import CheckBoxAnswer from "./CheckBoxAnswer"

const RadioForm = ({
    selectedQuestion,
    answerCollectionHandler,
})=>{
    /*---------------LOCAL STATE----------------*/
    const [possibleAnswers, setPossibleAnswers] = useState([]);
    const [selectedAnswers, setSelectedAnswers] = useState([]);
    /*---------------LIFECYCLE----------------*/

    useEffect(() => {
        console.log("RADIO FORM SELECTED QUESTION: ", selectedQuestion)
        setPossibleAnswers(selectedQuestion.answers)
        if(selectedQuestion.selectedAnswers){
            setSelectedAnswers(selectedQuestion.selectedAnswers)
        }
    }, [selectedQuestion])
    /*---------------HANDLERS----------------*/
    const answerUpdateHandler = (answer)=>{
        let updatedAnswers = [...selectedAnswers];
        let sameAnswersFound = updatedAnswers.filter(ans => answer.id===ans.id);
        if(sameAnswersFound.length){
            updatedAnswers = updatedAnswers.filter(ans => answer.id!==ans.id);
        } else {
            updatedAnswers = [...updatedAnswers, answer];
        }
        console.log("UPDATED SELECTED ANSWERS: ", updatedAnswers)
        answerCollectionHandler(updatedAnswers)
    }
    return (
    <Form className="radioform-container">
        <div className="question-container">
            {
                <div className="answers-container">
                    {
                        possibleAnswers.map((answer, index)=>{
                            return (
                                <CheckBoxAnswer
                                    key={index}
                                    selectedQuestion={selectedQuestion}
                                    answer={answer}
                                    answerUpdateHandler={answerUpdateHandler}
                                    selectedAnswers={selectedAnswers}
                                />
                            )
                        })
                    }
                </div>
            }
        </div>
    </Form>
    )
}

export default RadioForm;
