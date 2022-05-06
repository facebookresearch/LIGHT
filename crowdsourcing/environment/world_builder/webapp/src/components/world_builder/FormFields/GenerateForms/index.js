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
import Form from 'react-bootstrap/Form'
//BUTTON
import Button from 'react-bootstrap/Button'

/* CUSTOM COMPONENTS */

const GenerateForms = ({label, value, changeHandler, clickFunction})=> {
  return (
    <div className="generateform-container">
        <Form>
                <Row>
                    <Col xs={4}>
                        <Form.Label>{label}</Form.Label>
                    </Col>
                    <Col xs={6}/>
                    <Col xs={2}>
                        <Button onClick={clickFunction} variant="primary" type="submit">
                            Generate
                        </Button>
                    </Col>
                </Row>
                <Row style={{marginTop:"5px"}}>
                    <Col>
                        <Form.Control onChange={changeHandler} value={value} type={label} />
                    </Col>
                </Row>
        </Form>
    </div>

  );
}

export default GenerateForms;
