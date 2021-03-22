import React from "react";
import ButtonGroup from 'react-bootstrap/ButtonGroup';
import ToggleButton from 'react-bootstrap/ToggleButton';
import Form from 'react-bootstrap/Form';
import FormControl from 'react-bootstrap/FormControl';

function ConstraintToggleButton() {
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

function IsHoldingConstraint({ state }) {
    return (
        <div>
            <div className="title is-4">
                Is the actor holding the used item?
            </div>
            This action requires the actor to be holding {state['secondaryObject']}
            <ConstraintToggleButton />
        </div>
    );
};

function UsedWithItemConstraint({ state }) {
    return (
        <div>
            <div className="title is-4">
                Is the actor doing the action with a certain object?
            </div>
            This action requires the actor to be realizing the action with {state['secondaryObject']}. This action CANNOT be done with another object.
            <ConstraintToggleButton />
        </div>
    );
};

function UsedWithAgentConstraint({ state }) {
    return (
        <div>
            <div className="title is-4">
                Is the action being done with an agent?
            </div>
            This action requires {state['secondaryObject']} to be an agent (A living being).
            <ConstraintToggleButton />
        </div>
    );
};

function InRoomConstraint() {
    return (
        <div>
            <div className="title is-4">
                Is the action being done with an agent?
            </div>
            This action needs to be happening in the specific room:
            <Form inline>
                <Form.Control
                    className="mb-2 mr-sm-2"
                    id="inlineFormInputName2"
                    placeholder="Room"
                />
            </Form>
            <ConstraintToggleButton />
        </div>
    );
};

function ConstraintBlock({ state }) {
    return (
        <div>
            <div className="title is-4">
                Constraints
            </div>
            <hr/>
            <IsHoldingConstraint state={state} />
            <br />
            <UsedWithItemConstraint state={state} />
            <br />
            <UsedWithAgentConstraint state={state} />
            <br />
            <InRoomConstraint />
        </div>
    );
}

export { ConstraintBlock };