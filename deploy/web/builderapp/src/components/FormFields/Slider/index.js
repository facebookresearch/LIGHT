/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React, {useRef} from 'react';
/* REDUX */

/* STYLES */
import './styles.css';
/* BOOTSTRAP COMPONENTS */
//LAYOUT
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
//FORM
import Form from 'react-bootstrap/Form'
/* CUSTOM COMPONENTS */


const Slider = ({
    label,
    maxLabel,
    minLabel,
    value,
    min,
    max,
    changeHandler
})=> {
    

    return (
        <div className="slider-container">
            <Row>
                <h5>{label}</h5>
            </Row>
            <Row>
                <Col>
                    <Form.Label>{minLabel}</Form.Label>
                </Col>
                <Col xs={8}>
                    <Form.Range 
                        value={(value==null) ? (min+max)/2 : value}
                        onChange={changeHandler}
                        min={min}
                        max={max}
                    />
                </Col>
                <Col>
                <   Form.Label>{maxLabel}</Form.Label>
                </Col>
            </Row>
        </div>
    );
}

export default Slider;