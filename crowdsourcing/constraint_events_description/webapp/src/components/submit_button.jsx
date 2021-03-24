import React, { Component } from 'react';
import Button from 'react-bootstrap/Button';

function SubmitButton({ active, state, onSubmit }) {
    if (active) {
        return (
            <Button variant="primary" onClick={() => {onSubmit(state)}}>Submit</Button>
        );
    } else {
        return (
            <Button variant="secondary" disabled>Submit</Button>
        );
    }
}

export { SubmitButton };