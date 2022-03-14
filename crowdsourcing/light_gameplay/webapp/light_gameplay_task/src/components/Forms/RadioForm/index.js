import react from "react";

const RadioForm = ({questions})=>{

    return (
    <Form>
        {questions.map((question) => (
            <div className="mb-3">
                <Form.Label>{}</Form.Label>
                <Form.Check
                inline
                label="1"
                name="group1"
                type={'radio'}
                />
            </div>
        ))}
    </Form>
    )
}

export default RadioForm;
