/* REACT */
import React, {useRef} from 'react';
/* REDUX */
import {useAppDispatch, useAppSelector} from '../../../app/hooks';
/* STYLES */
import './styles.css';
/* BOOTSTRAP COMPONENTS */
//FORM
import Form from 'react-bootstrap/Form'
import FloatingLabel from 'react-bootstrap/FloatingLabel'
/* CUSTOM COMPONENTS */


const TextInput = ({
    label
})=> {
    const textInputRef = useRef(null);

    return (
        <div className="textinput-container">
            <FloatingLabel
                label={label}
                className="mb-3"
            >
                <Form.Control ref={textInputRef} type="text" placeholder={label} />
            </FloatingLabel>
        </div>
    );
}

export default TextInput;