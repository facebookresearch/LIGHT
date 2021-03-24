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

function CreateEntityEvent({ state, eventArray }) {
    const [toggleValue, setToggleValue] = React.useState("");
    const [name, setName] = React.useState("");
    const [description, setDescription] = React.useState("");

    const eventSet = {
        "active": toggleValue,
        "format": {
            "type": "create_entity",
            "params": {
                "type": "in_used_target_item",
                "object": {
                    "name": name,
                    "description": description
                }
            }
        }
    }

    eventArray.push(eventSet);

    return (
        <div>
            <div className="title is-4">
                An entity is created?
            </div>
            This action creates/spawns/reveals a new object:
            <Form>
                <Form.Group controlId="formBasicName">
                    <Form.Label>Name</Form.Label>
                    <Form.Control type="name" placeholder="Object Name" onChange={(e)=>{setName(e.target.value)}}/>
                </Form.Group>

                <Form.Group controlId="formBasicDescription">
                    <Form.Label>Description</Form.Label>
                    <Form.Control type="description" placeholder="Description" onChange={(e)=>{setDescription(e.target.value)}}/>
                </Form.Group>
            </Form>
            <br/>
            <EventToggleButton />
        </div>
    );
}

function BroadcastMessageEvent({ state, eventArray }) {
    const [toggleValue, setToggleValue] = React.useState("");
    const [roomView, setRoomView] = React.useState("");

    const eventSet = {
        "active": toggleValue,
        "format": {
            "type": "broadcast_message",
            "params": {
                "self_view": state['actionDescription'],
                "room_view": roomView
            }
        }
    }
    eventArray.push(eventSet);

    return (
        <div>
            <div className="title is-4">
                How others see this event?
            </div>
            Convert the action description <i>"{state.actionDescription}"</i> to third person, using "Actor" as the subject. Think as someone seeing the action:
            <Form>
                <Form.Group controlId="formBasicDescription">
                    <Form.Label>Action Description (Room View):</Form.Label>
                    <Form.Control style={{ width:"900px"}} type="name" placeholder="Action Description but with 'Actor' as subject" onChange={(e)=>{setRoomView(e.target.value)}}/>
                </Form.Group>
            </Form>
            <br />
            <EventToggleButton />
        </div>
    );
}

function ModifyAttributeEvent({ state, eventArray }) {
    const [toggleValue, setToggleValue] = React.useState("");
    const [attribute, onChangeAttribute] = React.useState("");
    const [attributeValue, onChangeAttributeValue] = React.useState("");

    const [target, onChangeTarget] = React.useState("");
    const targetList = ['actor', state["primaryObject"], state["secondaryObject"]];

    const eventSet = {
        "active": toggleValue,
        "format": {
            "type": "modify_attribute",
            "params": {
                "type": target === 'actor' ? "actor" : "in_used_target_item",
                "key": attribute,
                "value": "=" + attributeValue 
            }
        }
    }
    eventArray.push(eventSet);

    return (
        <div>
            <div className="title is-4">
                Does this action modifies an attribute of something involved in it?
            </div>
            <p>For example, when you kill someone with a sword, you modify the attribute "health" to 0!</p>
            <p>You will be given some attributes as examples for suggestion, but feel free to think about any attribute you would like to change.</p>
            <p>These attribute modifications can be applied to <b>three</b> possible members of the interaction: <b>Actor</b>, <b>{state["primaryObject"]}</b> or <b>{state["secondaryObject"]}</b></p>
            <br />
            <p>The object/agent </p> 
            <SingleSelector objectList={targetList} onChangeCurrentSelectedObject={onChangeTarget} />
            <p> has the attribute </p>
            <Form.Group controlId="formBasicAttribute" inline>
                    <Form.Control type="attribute" placeholder="Attribute" onChange={(e) => { onChangeAttribute(e.target.value); }}/>
            </Form.Group>
            <p> changed to </p>
            <Form.Group controlId="formBasicAttrValue" inline>
                    <Form.Control type="attributeValue" placeholder="Attribute Compare Value" onChange={(e) => { onChangeAttributeValue(e.target.value); }}/>
            </Form.Group>
            <br />
            <br />
            <EventToggleButton constraint="attributeCompareValue" />
        </div>
    );
}

function EventsBlock({ state, eventArray }) {
    return (
        <div>
            <div className="title is-4">
                <b>EVENTS</b>
            </div>
            <hr/>
            <CreateEntityEvent state={state} eventArray={eventArray} />
            <br />
            <BroadcastMessageEvent state={state} eventArray={eventArray} />
            <br />
            <ModifyAttributeEvent state={state} eventArray={eventArray} />
        </div>
    );
}

export { EventsBlock };