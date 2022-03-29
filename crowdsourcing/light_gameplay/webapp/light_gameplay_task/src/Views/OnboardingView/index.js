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
  const QUESTIONCOUNT = 3
    const getRandomNumber= (max)=> {
        return Math.floor(Math.random() * max);
    }


  /*---------------LOCAL STATE----------------*/
    const [questionBank, setQuestionBank] = useState([]);
    const [currentQuestionPosition, setCurrentQuestionPosition] = useState(0);
    const [selectedQuestion, setSelectedQuestion] = useState(null);
    const [answeredQuestions, setAnsweredQuestions] = useState([]);

  /*---------------HANDLERS----------------*/
    const QuestionChangeHandler = (direction)=>{
        let updatedQuestionPosition = currentQuestionPosition;
        if(direction==="previous"){
            updatedQuestionPosition = currentQuestionPosition - 1;
        }
        if(direction==="next"){
            updatedQuestionPosition = currentQuestionPosition + 1;
        }
        setCurrentQuestionPosition(updatedQuestionPosition);
        setSelectedQuestion(questionBank[updatedQuestionPosition])
    }

    const AnswerCollectionHandler = (answer)=>{
        let updatedAnsweredQuestion = selectedQuestion;
        updatedAnsweredQuestion.selectedAnswers = answer;
        let updatedAnswers = answeredQuestions.filter(answeredQuestion => (answeredQuestion.id===answer.id));
        updatedAnswers = [...updatedAnswers, updatedAnsweredQuestion];
        console.log("ANSWERED QUESTIONS: ", updatedAnswers)
        setAnsweredQuestions(updatedAnswers)
    }



    const SubmissionHandler = (direction)=>{
        let updatedQuestionPosition = currentQuestionPosition;
        if(direction==="previous"){
            updatedQuestionPosition = currentQuestionPosition - 1;
        }
        if(direction==="next"){
            updatedQuestionPosition = currentQuestionPosition + 1;
        }
        setCurrentQuestionPosition(updatedQuestionPosition);
        setSelectedQuestion(questionBank[updatedQuestionPosition])
    }

  /*---------------LIFECYCLE----------------*/


    useEffect(() => {
        let questions= TaskCopy
        let updatedQuestionBank =[]
        for(let i=0; i<QUESTIONCOUNT; i++){
            let remainingQuestionsCount = questions.length;
            let newSelectedQuestionIndex = getRandomNumber(remainingQuestionsCount);
            updatedQuestionBank.push(questions[newSelectedQuestionIndex]);
            questions = questions.filter((question, index)=> (index!==newSelectedQuestionIndex));
            console.log("next set of questions", questions)
        }
        console.log("UPDATED QUESTION BANK", updatedQuestionBank);
        setQuestionBank(updatedQuestionBank);
        let updatedCurrentQuestion = updatedQuestionBank[currentQuestionPosition];
        setSelectedQuestion(updatedCurrentQuestion)
    }, [])

  return (
    <div className="onboarding-container">
        <Navbar bg="dark" variant="dark">
            <div className="tool-container">
                <Navbar.Text>
                    <span className="task-label">GAMEPLAY TASK ONBOARDING</span>
                </Navbar.Text>
                <Navbar.Text>
                    <span>{` QUESTIONS ANSWERED: ${answeredQuestions.length}/${questionBank.length}`}</span>
                </Navbar.Text>
            </div>
        </Navbar>
        <div className="onboarding-body">
            {
                (selectedQuestion)
                ?
                <div className="onboarding-question">
                    <h5>Select the answer or answers that most appropriately fit an in character action or response.  Click Next to move on to the next question.  You can return to the previously answered questions at anytime but clicking the Submit button </h5>
                    <ChatQuestionDisplay
                        questionData={selectedQuestion.question}
                    >
                        <RadioForm
                            answerData={selectedQuestion.answers}
                            answerCollectionHandler = {AnswerCollectionHandler}
                        />
                    </ChatQuestionDisplay>
                    <div className="onboarding-buttons_container">
                        {
                            (currentQuestionPosition > 0)
                            ?
                            <Button
                                className="onboarding-button"
                                variant ="warning"
                                onClick={()=>QuestionChangeHandler("previous")}
                            >
                                Previous
                            </Button>
                            : <div/>
                        }
                        {
                            (currentQuestionPosition < questionBank.length-1)
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
