/* REACT */
import React, {useEffect, useState} from "react";
/* STYLES */
import "./styles.css";
/* CUSTOM COMPONENTS */
import RadioForm from "../../components/Forms/RadioForm";
import ChatQuestionDisplay from "../../components/ChatQuestionDisplay";
/* BOOTSTRAP COMPONENTS */
import Navbar from 'react-bootstrap/Navbar'
import Button from 'react-bootstrap/Button';
/* COPY */
import TaskCopy from "../../TaskCopy";


const OnboardingView = ()=>{
  /*---------------UTIL----------------*/
    const getRandomNumber= (max)=> {
        return Math.floor(Math.random() * max);
    }


  /*---------------LOCAL STATE----------------*/
    const [questionBank, setQuestionBank] = useState([]);
    const [currentQuestionId, setCurrentQuestionId] = useState(0);
    const [selectedQuestion, setSelectedQuestion] = useState(null);
    const [answeredQuestions, setAnsweredQuestions] = useState([]);

  /*---------------HANDLERS----------------*/
    const QuestionChangeHandler = (direction)=>{
        if(direction==="previous"){

        }
        if(direction==="next"){
            let remainingQuestionsCount = questionBank.length
            let newSelectedQuestionId = getRandomNumber(remainingQuestionsCount)
            console.log("ID", newSelectedQuestionId)
            let newSelectedQuestion = TaskCopy[newSelectedQuestionId]
            console.log("NEW QUESTION", newSelectedQuestion)
            let updatedAnsweredQuestions = [...answeredQuestions, newSelectedQuestion]
            let updatedQuestionBank = questionBank.filter((question, id) => (id!==newSelectedQuestionId))
            setQuestionBank(updatedQuestionBank)
            setAnsweredQuestions(updatedAnsweredQuestions)
            setSelectedQuestion(newSelectedQuestion)
        }
    }

  /*---------------LIFECYCLE----------------*/


    useEffect(() => {
        console.log(questionBank)
        let remainingQuestionsCount = TaskCopy.length
        let newSelectedQuestionId = getRandomNumber(remainingQuestionsCount)
        console.log("ID", newSelectedQuestionId)
        let newSelectedQuestion = TaskCopy[newSelectedQuestionId]
        console.log("NEW QUESTION", newSelectedQuestion)
        let updatedAnsweredQuestions = [...answeredQuestions, newSelectedQuestion]
        let updatedQuestionBank = questionBank.filter((question, index) => (index !== newSelectedQuestionId))
        console.log("updatedQuestionBank", updatedQuestionBank)
        setQuestionBank(updatedQuestionBank)
        setAnsweredQuestions(updatedAnsweredQuestions)
        setSelectedQuestion(newSelectedQuestion)
    }, [])

  return (
    <div className="onboarding-container">
        <Navbar bg="dark" variant="dark">
            <div className="tool-container">
                <Navbar.Text>
                    <span className="task-label">GAMEPLAY TASK ONBOARDING</span>
                </Navbar.Text>
                <Navbar.Text>
                    <span>{` QUESTIONS ANSWERED: ${answeredQuestions.length}/${TaskCopy.length}`}</span>
                </Navbar.Text>
            </div>
        </Navbar>
        <div className="onboarding-body">
            {
                (selectedQuestion !== null)
                ?
                <div className="onboarding-question">
                    <ChatQuestionDisplay
                        questionData={selectedQuestion.question}
                    >
                        <RadioForm
                            answerData={selectedQuestion.answers}
                        />
                    </ChatQuestionDisplay>
                    <div className="onboarding-buttons_container">
                        {
                            (currentQuestionId !== 0)
                            ?
                            <Button
                                className="onboarding-button"
                                variant ="warning"
                            >
                                Previous
                            </Button>
                            :null
                        }
                        {
                            questionBank.length
                            ?
                            <Button
                                className="onboarding-button"
                                onClick={()=>QuestionChangeHandler("next")}

                            >
                                Next
                            </Button>
                            :
                            <Button
                                className="onboarding-button"
                                variant ="success"
                            >
                            Submit
                        </Button>
                        }
                    </div>
                </div>
                :null
            }
        </div>
    </div>
  );
}

export default OnboardingView;
