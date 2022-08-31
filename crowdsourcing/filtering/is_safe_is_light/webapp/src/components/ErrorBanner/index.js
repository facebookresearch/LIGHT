
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
//ICONS
import { BsExclamationOctagonFill, BsCheck, BsX } from "react-icons/bs";

// ErrorToast - renders toast for user with relevant errors rendered as a bulleted list in the toast.
const ErrorBanner= ({
    errors, // Array of Errors from App state generated when user attempts an erroneous submission
    showError, //Boolean signaling toast to render.
    hideError, // Function that will hide toast upon clicking the x in the top right corner
})=>{
    return(
        <Alert variant="danger" dismissible id="toast-container" onClose={hideError} show={showError} >
            <div id="toast-header">
                <p id="toast-header__text">
                    ERROR
                </p>
            </div>
            <ul>
                {
                errors.map((err, index)=>(
                <li style={{width: "90vw"}} id="toast-error" key={index}>
                    {err}
                </li>
                ))
                }
            </ul>
        </Alert>
    )
}

export default ErrorBanner;
