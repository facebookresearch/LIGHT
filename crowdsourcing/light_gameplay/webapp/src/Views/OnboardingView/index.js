/* REACT */
import React, {useEffect, useState, useReducer} from "react";
/* STYLES */
import "./styles.css";
/* CUSTOM COMPONENTS */
import RadioForm from "../../components/Forms/RadioForm";
import ChatQuestionDisplay from "../../components/ChatQuestionDisplay";
import CollapsibleBox from "../../components/CollapsibleBox";
/* BOOTSTRAP COMPONENTS */
import Navbar from 'react-bootstrap/Navbar';
import Button from 'react-bootstrap/Button';
import Modal from 'react-bootstrap/Modal';
/* COPY */
import TaskCopy from "../../TaskCopy";

const OnboardingView = ({
    onBoardingSubmitFunction
})=>{
  /*---------------UTIL----------------*/
    const QUESTIONCOUNT = 3 //Questions being pulled from Task Copy
    const ANSWERCOUNT = 4 // Answers being pulled from Question
    //getRandomNumber - generates integer between 0 and argument given.
    const getRandomNumber= (max)=> {
        return Math.floor(Math.random() * max);
    }

/*---------------LOCAL STATE----------------*/
    const [questionBank, setQuestionBank] = useState([]);//Questions being used in session
    const [currentQuestionPosition, setCurrentQuestionPosition] = useState(0);// Sets Selected question using this value as the index in the questiion bank array
    const [selectedQuestion, setSelectedQuestion] = useState(null); //Question Data displayed to user
    const [answeredQuestions, setAnsweredQuestions] = useState(0); // Questions and answer that
    const [showModal, setShowModal] = useState(false);
/*---------------REDUCERS----------------*/
// [answers, updateAnswer] = useReducer(
//     (oldAnswers, newAnswer) => {
//         return oldAnswers.map((answer, idx) => (idx == currentQuestionPosition) ? newAnswer : answer);
//     },
//     getEmptyAnswers(),
// ) # NOTE: Discuss with Jack
/*---------------HANDLERS----------------*/
    const handleCloseModal = () => setShowModal(false);
    const handleShowModal = () => setShowModal(true);
    const QuestionChangeHandler = (direction)=>{
        let updatedQuestionPosition = currentQuestionPosition;
        if(direction==="previous"){
            updatedQuestionPosition = currentQuestionPosition - 1;
        }
        if(direction==="next"){
            updatedQuestionPosition = currentQuestionPosition + 1;
        }
        setCurrentQuestionPosition(updatedQuestionPosition);
    }
    // AnswerCollectionHandler - updates questionBank object with selectedAnswers key
    const AnswerCollectionHandler = (answers)=>{
        let updatedAnsweredQuestion = selectedQuestion;
        updatedAnsweredQuestion.selectedAnswers = answers;
        let updatedQuestions = questionBank.map(question => {
            if(question.id !== updatedAnsweredQuestion.id){
                return question
            }else{
                return updatedAnsweredQuestion
            }
        });
        let updatedQuestionBank = updatedQuestions;
        setQuestionBank(updatedQuestionBank)
    }

    const SubmissionHandler = ()=>{
       console.log("ANSWER SUBMISSION:  ", questionBank)
       onBoardingSubmitFunction(questionBank)
    }

  /*---------------LIFECYCLE----------------*/
    useEffect(() => {
        let updatedAnsweredQuestionCount = questionBank.filter(question=>{
            let {selectedAnswers} = question;
            let isAnswered = selectedAnswers ? selectedAnswers : [];
            return (isAnswered.length>0);
        })
        setAnsweredQuestions(updatedAnsweredQuestionCount.length)
        let updatedCurrentQuestion = questionBank[currentQuestionPosition];
        setSelectedQuestion(updatedCurrentQuestion)
    }, [questionBank])

    useEffect(() => {
        let updatedCurrentQuestion = questionBank[currentQuestionPosition];
        setSelectedQuestion(updatedCurrentQuestion)
    }, [currentQuestionPosition])

    useEffect(() => {
        let updatedAnsweredQuestionCount = questionBank.filter(question=>{
            let {selectedAnswers} = question;
            let isAnswered = selectedAnswers ? selectedAnswers : [];
            return isAnswered.length
        })
        setAnsweredQuestions(updatedAnsweredQuestionCount.length)
    }, [selectedQuestion])

    useEffect(() => {
        let questions= TaskCopy
        let updatedQuestionBank =[]
        for(let i=0; i<QUESTIONCOUNT; i++){
            let remainingQuestionsCount = questions.length;
            let newSelectedQuestionIndex = getRandomNumber(remainingQuestionsCount);
            let formattedQuestion = questions[newSelectedQuestionIndex];
            let formattedAnswers =[];
            let answerBank = formattedQuestion.answers;
            for(let i=0; i<ANSWERCOUNT; i++){
                let remainingAnswersCount = answerBank.length;
                let newSelectedAnswerIndex = getRandomNumber(remainingAnswersCount);
                formattedAnswers.push(answerBank[newSelectedAnswerIndex]);
                answerBank = answerBank.filter((answer, index)=> (index!==newSelectedAnswerIndex));
            }
            formattedQuestion.answers = formattedAnswers;
            updatedQuestionBank.push(questions[newSelectedQuestionIndex]);
            questions = questions.filter((question, index)=> (index!==newSelectedQuestionIndex));
        }
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
                    <span>{` QUESTIONS ANSWERED: ${answeredQuestions}/${questionBank.length}`}</span>
                </Navbar.Text>
            </div>
        </Navbar>
        <div className="onboarding-body">
            {
                (selectedQuestion)
                ?
                <div className="onboarding-info_container">
                    <CollapsibleBox
                        titleBg={"gold"}
                        title={`${selectedQuestion.character.name}`}
                        containerBg="#e0fffe"
                    >
                        <p style={{ fontSize: "16px"}}>
                            {selectedQuestion.character.description.slice(
                                0,
                                selectedQuestion.character.description.indexOf("Your Mission:")
                            )}
                        </p>
                    </CollapsibleBox>
                    <CollapsibleBox
                        title={`Location:  ${selectedQuestion.setting.name}`}
                        titleBg="#76dada"
                        containerBg="#e0fffe"
                    >
                        <h3
                            style={{
                            textDecoration: "underline",
                            backgroundColor: "none",
                            fontFamily: "fantasy",
                            marginBottom: "0px",
                            }}
                        >
                        </h3>
                        {selectedQuestion.setting.description.split("\n").map((para, idx) => (
                            <p key={idx}>{para}</p>
                        ))}
                    </CollapsibleBox>
                </div>
                :null
            }
            {
                (selectedQuestion)
                ?
                <div className="onboarding-question">
                    <h5>Select all answers that fit an in character action or response for the given scenario with the above context.  Click Next to move on to the next question.  You can return to the previously answered questions at anytime before clicking the Submit button </h5>
                    <ChatQuestionDisplay
                        questionData={selectedQuestion.question}
                    >
                        <RadioForm
                            questionBank={questionBank}
                            selectedQuestion={selectedQuestion}
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
                                onClick={handleShowModal}
                                disabled={((answeredQuestions/questionBank.length)===1) ? false : true }
                            >
                            Submit
                        </Button>
                        }
                    </div>
                </div>
                :null
            }
        </div>
        <Modal show={showModal} onHide={handleCloseModal}>
            <Modal.Header closeButton>
                <Modal.Title
                    variant="success"
                >SUBMISSION CONFIRMATION</Modal.Title>
            </Modal.Header>
            <Modal.Body>
                Are you sure you are ready to submit your answers?  You will not be able to change them again.
            </Modal.Body>
            <Modal.Footer>
                <Button variant="secondary" onClick={handleCloseModal}>
                    Go Back
                </Button>
                <Button variant="success" onClick={SubmissionHandler}>
                    Submit Answers
                </Button>
            </Modal.Footer>
        </Modal>
    </div>
  );
}

export default OnboardingView;
