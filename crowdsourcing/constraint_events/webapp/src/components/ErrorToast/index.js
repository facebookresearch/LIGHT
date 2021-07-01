//REACT
import React, {useState} from "react";
//STYLING
import "./styles.css"
//BOOTSTRAP COMPONENTS
import Toast from 'react-bootstrap/Toast'

const ErrorToast = ({
    errors,
    showError,
    hideErrors,
})=>{


    return(
        <Toast>
            <Toast.Body>
                <ul>
                    {
                    errors.map((err, index)=>(
                    <li key={index}>
                        {err}
                    </li>
                    ))
                    }
                </ul>
            </Toast.Body>
        </Toast>
    )}

export default ErrorToast
