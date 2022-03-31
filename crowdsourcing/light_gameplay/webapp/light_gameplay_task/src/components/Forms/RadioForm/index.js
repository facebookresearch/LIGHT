/* REACT */
import react, {useState, useEffect} from "react";

/* STYLES */
import "./styles.css";
/* BOOTSTRAP COMPONENTS */
import Form from 'react-bootstrap/form';
/* CUSTOM COMPONENTS */
import CheckBoxAnswer from "./CheckBoxAnswer"

const RadioForm = ({
    answerData,
    answerCollectionHandler,
    currentlySelectedAnswers
})=>{
    /*---------------LOCAL STATE----------------*/
      const [selectedAnswers, setSelectedAnswers] = useState([])
    /*---------------LIFECYCLE----------------*/

    useEffect(() => {
        if(currentlySelectedAnswers){
            setSelectedAnswers(currentlySelectedAnswers)
        }
    }, [currentlySelectedAnswers])
    /*---------------HANDLERS----------------*/
    const answerUpdateHandler = (answer)=>{
        let updatedAnswers = selectedAnswers;
        let isNew = false;
        updatedAnswers.map(currentAnswer => {
            if(answer.id !== currentAnswer.id ){
                return currentAnswer;
            }else {
                isNew = true;
            }
        })
        if(isNew){
            console.log("IS NEW ANSWER")
            updatedAnswers = [...updatedAnswers, answer];
        }
        answerCollectionHandler(updatedAnswers)
    }
    return (
    <Form className="radioform-container">
        <div className="question-container">
            {
                <div className="answers-container">
                    {
                        answerData.map((answer, index)=>{
                            return (
                                <CheckBoxAnswer
                                    key={index}
                                    answer={answer}
                                    answerUpdateHandler={answerUpdateHandler}
                                    currentlySelectedAnswers={selectedAnswers}
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
