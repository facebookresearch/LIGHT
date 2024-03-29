/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

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