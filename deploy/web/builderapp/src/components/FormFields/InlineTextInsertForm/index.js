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
    formText,
    value,
    changeHandler,
    textPlacement
})=> {

    return (
        <Row className="inlinetextinsertform-container">
            {
                textPlacement=="before"
            ?
            <>
                <Col xs={2}>
                    <h5>{formText}</h5>
                </Col>
                <Col xs={10}>
                    <Form.Control value={value} onChange={changeHandler} type="text" />
                </Col>
            </>
            :
            <>
                <Col xs={2}>
                    <Form.Control value={value} onChange={changeHandler} type="text" />
                </Col>
                <Col xs={10}>
                    <h5>{formText}</h5>
                </Col>
            </>
            }
        </Row>
    );
}

export default InlineTextInsertForm;