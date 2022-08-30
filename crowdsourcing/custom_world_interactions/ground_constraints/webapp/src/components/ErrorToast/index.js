
/*****
 * Copyright (c) Meta Platforms, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

//REACT
import React, {useState} from "react";
//STYLING
import "./styles.css"
//BOOTSTRAP COMPONENTS
import Alert from 'react-bootstrap/Alert'
// ErrorToast - renders toast for user with relevant errors rendered as a bulleted list in the toast.
const ErrorToast= ({
    errors, // Array of Errors from App state generated when user attempts an erroneous submission
    showError, //Boolean signaling toast to render.
    hideError, // Function that will hide toast upon clicking the x in the top right corner
})=>{
    return(
        <Alert variant="danger" dismissible className="toast-container" onClose={hideError} show={showError} >
            <p className="toast-header">
                ERROR
            </p>
                <ul>
                    {
                    errors.map((err, index)=>(
                    <li style={{width: "90vw"}} className={"toast-error"} key={index}>
                        {err}
                    </li>
                    ))
                    }
                </ul>

        </Alert>
    )}

export default ErrorToast
