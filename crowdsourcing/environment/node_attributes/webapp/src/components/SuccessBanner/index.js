
/*****
 * Copyright (c) Meta Platforms, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

//REACT
import React from "react";
//STYLES
import "./styles.css";
//BOOTSTRAP
import Toast from 'react-bootstrap/Toast';
//ICONS
import { BsExclamationOctagonFill, BsCheck, BsX } from "react-icons/bs";


const SuccessBanner = ({
    showSuccess,
    toggleShowSuccess,
    successMessage
})=>{
    return (
        <>
            <Toast className="successbanner-container" show={showSuccess} onClose={toggleShowSuccess} delay={3000} autohide >
                <Toast.Header className="successbanner-header" closeButton={false}>
                    <BsCheck color="white" style={{fontSize:"18px"}}/>
                    <strong className="mr-auto">SUCCESS</strong>
                    <BsX color="white" onClick={toggleShowSuccess} style={{fontSize:"18px"}}/>
                </Toast.Header>
                <Toast.Body className="successbanner-body">
                    {successMessage}
                </Toast.Body>
            </Toast>
        </>
    )
}
export default SuccessBanner;
