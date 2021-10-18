/* REACT */
import React, {useRef} from 'react';
/* REDUX */
import {useAppDispatch, useAppSelector} from '../../../app/hooks';
/* STYLES */
import './styles.css';
/* BOOTSTRAP COMPONENTS */
//LAYOUT
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
//FORM
import Form from 'react-bootstrap/Form'
/* CUSTOM COMPONENTS */


const Slider = ({
    label,
    maxLabel,
    minLabel
})=> {
    const SliderRef = useRef(null);

    return (
        <div className="slider-container">
            <Row>
                <Form.Label>{label}</Form.Label>
            </Row>
            <Row>
                <Col>
                    <Form.Label>{minLabel}</Form.Label>
                </Col>
                <Col>
                <Form.Range ref={SliderRef} />
                </Col>
                <Col>
                <   Form.Label>{maxLabel}</Form.Label>
                </Col>
            </Row>
        </div>
    );
}

export default Slider;