import React from "react";
import ButtonGroup from 'react-bootstrap/ButtonGroup';
import ToggleButton from 'react-bootstrap/ToggleButton';
import Form from 'react-bootstrap/Form';

function EventToggleButton() {
    const [toggleValue, setToggleValue] = React.useState("");

    const values = [
        { name: 'True', value: '1'},
        { name: 'False', value: '0'}
    ];

    return (
        <div>
            <ButtonGroup toggle>
                {values.map((value, idx) => (
                    <ToggleButton
                        key={idx}
                        type="radio"
                        variant="secondary"
                        name="value"
                        value={value.value}
                        checked={toggleValue === value.value}
                        onChange={(e) => setToggleValue(e.currentTarget.value)}
                    >
                        {value.name}
                    </ToggleButton>  
                ))}
            </ButtonGroup>
        </div>
    );
}

function CreateEntityEvent({ state }) {
    return (
        <div>
            <div className="title is-4">
                An entity is created?
            </div>
            This action creates/spawns/reveals a new object:
            <Form>
                <Form.Group controlId="formBasicName">
                    <Form.Label>Name</Form.Label>
                    <Form.Control type="name" placeholder="Object Name" />
                </Form.Group>

                <Form.Group controlId="formBasicDescription">
                    <Form.Label>Description</Form.Label>
                    <Form.Control type="description" placeholder="Description" />
                </Form.Group>

                <Form.Group controlId="formBasicNamePrefix">
                    <Form.Label>Name Prefix</Form.Label>
                    <Form.Control type="nameprefix" placeholder="Name Prefix (An/A/The)" />
                </Form.Group>

                <Form.Group controlId="formBasicDescription">
                    <Form.Label>Is Wearable?</Form.Label>
                    <EventToggleButton />
                </Form.Group>
            </Form>
            <br/>
            <p>Does this event is necessary?</p>
            <EventToggleButton />
        </div>
    );
}

function EventsBlock({ state }) {
    return (
        <div>
            <div className="title is-4">
                Events
            </div>
            <hr/>
            <CreateEntityEvent state={state} />
        </div>
    );
}

export { EventsBlock };