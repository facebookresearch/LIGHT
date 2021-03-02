
import React, { Component } from 'react';
import Form from 'react-bootstrap/Form';

function InteractionDescription() {
    return (
        <Form>
            <Form.Group controlId="exampleForm.ControlTextarea1">
                <Form.Label>Example textarea</Form.Label>
                <Form.Control as="textarea" rows={3} placeholder="Describe (in text format) the interaction between these two objects" />
            </Form.Group>
        </Form>
    );
}

export { InteractionDescription };
