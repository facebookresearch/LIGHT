
import React, { Component } from 'react';
import Form from 'react-bootstrap/Form';

function InteractionDescription({ description, onChangeDescription }) {
    return (
        <Form>
            <Form.Group controlId="exampleForm.ControlTextarea1">
                <Form.Label>Action Description (Second Person):</Form.Label>
                <Form.Control
                    as="textarea"
                    rows={3}
                    placeholder="Describe (in text format) the interaction between these two objects"
                    onChange={(e) => onChangeDescription(e.target.value)}
                />
            </Form.Group>
        </Form>
    );
}

export { InteractionDescription };
