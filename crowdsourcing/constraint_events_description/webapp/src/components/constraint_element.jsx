import React from "react";
import ButtonGroup from 'react-bootstrap/ButtonGroup';
import ToggleButton from 'react-bootstrap/ToggleButton';
import Form from 'react-bootstrap/Form';

function ConstraintToggleButton({ constraintName }) {
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
                        name={constraintName}
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

function SingleSelector({objectList, onChangeCurrentSelectedObject}) {
    const selectorList = [];
    
    for (const [index, object] of objectList.entries()) {
      selectorList.push(
        <option key={index} value={object}>{object}</option>
      )
    }
  
    return (
      <Form.Control as="select" onChange={(e) => { onChangeCurrentSelectedObject(e.target.value); }}>
        <option key={-1} value={""}>Select one</option>
        {selectorList}
      </Form.Control>
    );
  }

function IsHoldingConstraint({ state }) {
    return (
        <div>
            <div className="title is-4">
                Is the actor holding the used item?
            </div>
            This action requires the actor to be holding {state['secondaryObject']}
            <ConstraintToggleButton constraintName="isHolding"/>
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
            <ConstraintToggleButton constraintName="usedWithItem"/>
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
            <ConstraintToggleButton constraintName="usedWithAgent"/>
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
            <ConstraintToggleButton constraintName="inRoom"/>
        </div>
    );
};

function AttributeCompareValueConstraint({ state }) {
    const [attributeName, onChangeAttributeName] = React.useState("");
    const [attributeValue, onChangeAttributeValue] = React.useState("");

    const [cmp, onChangeCmp] = React.useState('equal');
    const cmpList = ['equal', 'not equal', 'greater', 'greater than or equal', 'less', 'less than or equal'];

    const [target, onChangeTarget] = React.useState("");
    const targetList = ['actor', state["primaryObject"], state["secondaryObject"]]

    return (
        <div>
            <div className="title is-4">
                Does this action requires that an element involved (The actor or one of the objects) has an attribute restriction?
            </div>
            <p>For example, in order to kill someone with a sword, it needs to be alive. Therefore, the attribute "health" needs to greater than 0!</p>
            <p>You will be given some attributes as examples for restrictions, but feel free to think about any restriction you would like.</p>
            <p>The restrictions can be applied to <b>three</b> possible members of the interaction: <b>Actor</b>, <b>{state["primaryObject"]}</b> or <b>{state["secondaryObject"]}</b></p>
            <br />
            <p>The object/agent </p> 
            <SingleSelector objectList={targetList} onChangeCurrentSelectedObject={onChangeTarget} />
            <p> has the attribute </p>
            <Form.Group controlId="formBasicAttribute" inline>
                    <Form.Control type="attribute" placeholder="Attribute" onChange={(e) => { onChangeAttributeName(e.target.value); }}/>
            </Form.Group>
            <p> which needs to be </p>
            <SingleSelector objectList={cmpList} onChangeCurrentSelectedObject={onChangeCmp} />
            <p> when compared to</p>
            <Form.Group controlId="formBasicAttrValue" inline>
                    <Form.Control type="attributeValue" placeholder="Attribute Compare Value" onChange={(e) => { onChangeAttributeValue(e.target.value); }}/>
            </Form.Group>
            <br />
            <br />
            <ConstraintToggleButton constraint="attributeCompareValue" />
        </div>
    );
}

function ConstraintBlock({ state }) {
    return (
        <div>
            <div className="title is-4">
                <b>CONSTRAINT</b>
            </div>
            <hr/>
            <IsHoldingConstraint state={state} />
            <br />
            <UsedWithItemConstraint state={state} />
            <br />
            <UsedWithAgentConstraint state={state} />
            <br />
            <InRoomConstraint />
            <br />
            <AttributeCompareValueConstraint state={state} />
        </div>
    );
}

export { ConstraintBlock };