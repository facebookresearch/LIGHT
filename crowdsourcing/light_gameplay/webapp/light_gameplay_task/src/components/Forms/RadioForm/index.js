import react from "react";
/* BOOTSTRAP COMPONENTS */
import Form from 'react-bootstrap/form'

const RadioForm = ({questions})=>{

    return (
    <Form>
        {
            questions.length
            ?
            questions.map((questionObj) => {
                let {question, answers}= questionObj
                return (
                    <div className="mb-3">
                        <Form.Label>{}</Form.Label>
                        <img src={question} />
                        {
                            answers.map(answer=>(
                                <Form.Check
                                inline
                                type={'radio'}
                                >
                                    <img src={answer} />
                                </Form.Check>
                            ))
                        }
                    </div>
                )
            })
            :
            null
        }
    </Form>
    )
}

export default RadioForm;
