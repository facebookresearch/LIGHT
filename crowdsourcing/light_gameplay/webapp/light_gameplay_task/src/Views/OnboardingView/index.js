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


  /*---------------LOCAL STATE----------------*/
    const selectedQuestion = useState(null)


  /*---------------HANDLERS----------------*/


  /*---------------LIFECYCLE----------------*/
    useEffect(() => {

        return () => {

        }
    }, [])

  return (
    <div className="onboarding-container">
        <Navbar bg="dark" variant="dark">
            <div className="tool-container">
                <Navbar.Text>
                    <span className="task-label">GAMEPLAY TASK ONBOARDING</span>
                </Navbar.Text>
            </div>
        </Navbar>
        <div className="onboarding-body">
            <div className="onboarding-question">
                <ChatQuestionDisplay
                    questionData={TaskCopy[0].question}
                >
                    <RadioForm
                        answerData={TaskCopy[0].answers}
                    />
                </ChatQuestionDisplay>
            </div>
        </div>
    </div>
  );
}

export default OnboardingView;
