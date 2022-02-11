/* REACT */
import React, {useRef} from 'react';
/* REDUX */
import {useAppDispatch, useAppSelector} from '../../../app/hooks';
/* STYLES */
import './styles.css';
/* BOOTSTRAP COMPONENTS */
//LAYOUT
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
//FORM
import Form from 'react-bootstrap/Form'
import FloatingLabel from 'react-bootstrap/FloatingLabel'
/* CUSTOM COMPONENTS */


const InlineTextInsertForm = ({
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

export default InlineTextInsertForm;