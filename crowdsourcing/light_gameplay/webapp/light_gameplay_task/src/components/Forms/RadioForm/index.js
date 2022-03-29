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

})=>{
    /*---------------UTIL----------------*/
    const ANSWERCOUNT = 4
    const getRandomNumber= (max)=> {
        return Math.floor(Math.random() * max);
    }
    /*---------------LOCAL STATE----------------*/
      const [answerBank, setAnswerBank] = useState([]);
    /*---------------LIFECYCLE----------------*/
    useEffect(() => {
        let answers= answerData
        let updatedAnswerBank =[]
        for(let i=0; i<ANSWERCOUNT; i++){
            let remainingAnswersCount = answers.length;
            let newSelectedAnswerIndex = getRandomNumber(remainingAnswersCount);
            updatedAnswerBank.push(answers[newSelectedAnswerIndex]);
            answers = answers.filter((answer, index)=> (index!==newSelectedAnswerIndex));
            console.log("next set of answers", answers)
        }
        console.log("UPDATED ANSWERS BANK", updatedAnswerBank);
        setAnswerBank(updatedAnswerBank);
    }, [answerData])
    return (
    <Form className="radioform-container">
        <div className="question-container">
            {
                <div className="answers-container">
                    {
                        answerBank.map((answer, index)=>(
                            <CheckBoxAnswer
                                key={index}
                                answer={answer}
                            />
                        ))
                    }
                </div>
            }
        </div>
    </Form>
    )
}

export default RadioForm;
