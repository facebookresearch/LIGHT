//REACT
import React, {useState} from "react";
//STYLING
import "./styles.css"
//BOOTSTRAP COMPONENTS
import Alert from 'react-bootstrap/Alert'

const ErrorToast= ({
    errors,
    showError,
    hideError,
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
