/* REACT */
import React, { useState } from 'react';
import Alert from 'react-bootstrap/Alert';
import Button from 'react-bootstrap/Button';

const ErrorAlert = ({
    closeFunction,
    showAlert
})=> {
    return (
    <>
        {
            showAlert
            ?
            <div className="alert-container">
                <Alert variant="danger" onClose={() => setShow(false)} dismissible>
                    <Alert.Heading>Oh snap! You got an error!</Alert.Heading>
                    <p>
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
