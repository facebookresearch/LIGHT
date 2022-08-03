/* REACT */
import React from 'react';
/* REDUX */

/* STYLES */
import './styles.css';
/* BOOTSTRAP COMPONENTS */
//LAYOUT
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
//FORM
import Form from 'react-bootstrap/Form';
//BUTTON
import Button from 'react-bootstrap/Button';
//SPINNER
import Spinner from 'react-bootstrap/Spinner';
/* CUSTOM COMPONENTS */
import GenerateButton from "../../Buttons/GenerateButton";

const GenerateForms = ({
    label,
    value,
    changeHandler,
    clickFunction,
    generateButtonLabel,
    isLoading
})=> {

  return (
    <Container className="generateform-container">
        <Form>
                <Row>
                    <Col xs={4}>
                        <Form.Label>{label}</Form.Label>
                    </Col>

                    <Col xs={2}>
                        <GenerateButton
                            clickFunction={clickFunction}
                            label ={generateButtonLabel}
                            isLoading={isLoading}
                        />
                    </Col>
                </Row>
                <Row style={{marginTop:"5px"}}>
                    <Col>
                        <Form.Control onChange={changeHandler} value={value} type={label} />
                    </Col>
                </Row>
        </Form>
    </Container>

  );
}

export default GenerateForms;
