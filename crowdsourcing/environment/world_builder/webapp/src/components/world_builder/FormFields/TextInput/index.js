/* REACT */
import React, {useRef} from 'react';
/* STYLES */
import './styles.css';
/* BOOTSTRAP COMPONENTS */
//FORM
import Form from 'react-bootstrap/Form'
import FloatingLabel from 'react-bootstrap/FloatingLabel'
/* CUSTOM COMPONENTS */


const TextInput = ({
    label,
    value,
    changeHandler
})=> {
    const textInputRef = useRef(null);

    return (
        <div className="textinput-container">
            <FloatingLabel
                label={label}
                className="mb-3"
            >
                <Form.Control value={value} onChange={changeHandler} type="text" placeholder={label} />
            </FloatingLabel>
        </div>
    );
}

export default TextInput;