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
            <p>Is this event necessary?</p>
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
            </Form>
            <br/>
            <EventToggleButton />
        </div>
    );
}

function BroadcastMessageEvent({ state }) {
    return (
        <div>
            <div className="title is-4">
                How others see this event?
            </div>
            Convert the action description <i>"{state.actionDescription}"</i> to third person, using "Actor" as the subject. Think as someone seeing the action:
            <Form>
                <Form.Group controlId="formBasicDescription">
                    <Form.Label>Action Description (Room View):</Form.Label>
                    <Form.Control style={{ width:"900px"}} type="name" placeholder="Action Description but with 'Actor' as subject" />
                </Form.Group>
            </Form>
            <br />
            <EventToggleButton />
        </div>
    );
}

function EventsBlock({ state }) {
    return (
        <div>
            <div className="title is-4">
                <b>EVENTS</b>
            </div>
            <hr/>
            <CreateEntityEvent state={state} />
            <br />
            <BroadcastMessageEvent state={state} />
        </div>
    );
}

export { EventsBlock };