import React from "react";
import ButtonGroup from 'react-bootstrap/ButtonGroup';
import ToggleButton from 'react-bootstrap/ToggleButton';
import Form from 'react-bootstrap/Form';

function ConstraintToggleButton({ constraintName, toggleValue, setToggleValue }) {
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

function IsHoldingConstraint({ state, constraintArray }) {
    const [toggleValue, setToggleValue] = React.useState("");
    
    const constraintSet = { 
        "active": toggleValue,
        "format": 
        {
            "type": "is_holding",
            "params": {
                "complement": "used_item"
            }
        }
    }

    constraintArray.push(constraintSet);

    return (
        <div>
            <div className="title is-4">
                Is the actor holding the used item?
            </div>
            This action requires the actor to be holding {state['secondaryObject']}
            <ConstraintToggleButton constraintName="isHolding" toggleValue={toggleValue} setToggleValue={setToggleValue}/>
        </div>
    );
};

function UsedWithItemConstraint({ state, constraintArray }) {
    const [toggleValue, setToggleValue] = React.useState("");

    const constraintSet = {
        "active": toggleValue,
        "format":
        {
            "type": "used_with_item_name",
            "params": {
                "item": state["secondaryObject"]
            }
        }
    }

    constraintArray.push(constraintSet);

    return (
        <div>
            <div className="title is-4">
                Is the actor doing the action with a certain object?
            </div>
            This action requires the actor to be realizing the action with {state['secondaryObject']}. This action CANNOT be done with another object.
            <ConstraintToggleButton constraintName="usedWithItem" toggleValue={toggleValue} setToggleValue={setToggleValue}/>
        </div>
    );
};

function UsedWithAgentConstraint({ state, constraintArray }) {
    const [toggleValue, setToggleValue] = React.useState("");

    const constraintSet = {
        "active": toggleValue,
        "format":
        {
            "type": "used_with_agent"
        }
    }
    constraintArray.push(constraintSet);

    return (
        <div>
            <div className="title is-4">
                Is the action being done with an agent?
            </div>
            This action requires {state['secondaryObject']} to be an agent (A living being).
            <ConstraintToggleButton constraintName="usedWithAgent" toggleValue={toggleValue} setToggleValue={setToggleValue}/>
        </div>
    );
};

function InRoomConstraint({ constraintArray }) {
    const [toggleValue, setToggleValue] = React.useState("");
    const [roomName, setRoomName] = React.useState("");

    const constraintSet = {
        "active": toggleValue,
        "format":
        {
            "type": "in_room",
            "params": {
                "room_name": roomName
            }
        }
    }
    constraintArray.push(constraintSet);

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
                    onChange={(e)=>{setRoomName(e.target.value);}}
                />
            </Form>
            <ConstraintToggleButton constraintName="inRoom" toggleValue={toggleValue} setToggleValue={setToggleValue}/>
        </div>
    );
};

function AttributeCompareValueConstraint({ state, constraintArray }) {
    const [toggleValue, setToggleValue] = React.useState("");
    const [attributeName, onChangeAttributeName] = React.useState("");
    const [attributeValue, onChangeAttributeValue] = React.useState("");

    const [cmp, onChangeCmp] = React.useState('equal');
    const cmpList = ['equal', 'not equal', 'greater', 'greater than or equal', 'less', 'less than or equal'];

    const [target, onChangeTarget] = React.useState("");
    const targetList = ['actor', state["primaryObject"], state["secondaryObject"]];

    const constraintSet = {
        "active": toggleValue,
        "format": {
            "type": "attribute_compare_value",
            "params": {
                "type": target === 'actor' ? "in_actor": "in_used_target_item",
                "key": attributeName,
                "list": [ attributeValue ],
                "cmp_type": cmp
            }
        }
    }
    constraintArray.push(constraintSet);

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
            <ConstraintToggleButton constraint="attributeCompareValue" toggleValue={toggleValue} setToggleValue={setToggleValue}/>
        </div>
    );
}

function ConstraintBlock({ state, constraintArray }) {
    console.log("constraint array: ", constraintArray);

    return (
        <div>
            <div className="title is-4">
                <b>CONSTRAINT</b>
            </div>
            <hr/>
            <IsHoldingConstraint state={state} constraintArray={constraintArray} />
            <br />
            <UsedWithItemConstraint state={state} constraintArray={constraintArray} />
            <br />
            <UsedWithAgentConstraint state={state} constraintArray={constraintArray} />
            <br />
            <InRoomConstraint constraintArray={constraintArray}/>
            <br />
            <AttributeCompareValueConstraint state={state} constraintArray={constraintArray}/>
        </div>
    );
}

export { ConstraintBlock };