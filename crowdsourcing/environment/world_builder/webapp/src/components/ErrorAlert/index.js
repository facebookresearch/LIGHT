/* REACT */
import React, { useState } from 'react';
/* BOOTSTRAP COMPONENTS */
import Alert from 'react-bootstrap/Alert';
/* STYLES */
import "./styles.css";

const ErrorAlert = ({
    closeFunction,
    showAlert,
    errorMessage
})=> {
    return (
    <>
        {
            showAlert
            ?
            <div className="alert-container">
                <Alert variant="danger" onClose={closeFunction} dismissible>
                    <Alert.Heading>Oh snap! You got an error!</Alert.Heading>
                    <p>
                        {errorMessage}
                    Change this and that and try again. Duis mollis, est non commodo
                    luctus, nisi erat porttitor ligula, eget lacinia odio sem nec elit.
                    Cras mattis consectetur purus sit amet fermentum.
                    </p>
                </Alert>
            </div>
            :
            null
        }
    </>
    );
}

export default ErrorAlert;
