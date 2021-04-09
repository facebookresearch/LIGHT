import React, { Component } from "react";
import Button from "react-bootstrap/Button";
import Form from "react-bootstrap/Form";

function SingleSelector({ objectList, onChangeCurrentSelectedObject }) {
  const selectorList = [];

  for (const [index, object] of objectList.entries()) {
    selectorList.push(
      <option key={index} value={object}>
        {object}
      </option>
    );
  }

  return (
    <Form.Control
      as="select"
      onChange={(e) => {
        onChangeCurrentSelectedObject(e.target.value);
      }}
    >
      <option key={-1} value={""}>
        Select one
      </option>
      {selectorList}
    </Form.Control>
  );
}

function OtherSecondaryForm({ onChangeCurrentSecondaryObject }) {
  return (
    <Form.Control
      as="textarea"
      style={{ width: "200px", height: "50px" }}
      rows={1}
      placeholder="Please use a medieval-fantasy themed object!"
      onChange={(e) => onChangeCurrentSecondaryObject(e.target.value)}
    />
  );
}

function ObjectSelector({
  primaryObjectList,
  secondaryObjectList,
  onChangeCurrentPrimaryObject,
  onChangeCurrentSecondaryObject,
  otherActive,
  onChangeOtherActive,
}) {
  return (
    <div className="menu">
      <Form.Group controlId="exampleForm.ControlSelect1">
        <Form.Label>Primary Object: </Form.Label>
        <br />
        <SingleSelector
          objectList={primaryObjectList}
          onChangeCurrentSelectedObject={onChangeCurrentPrimaryObject}
        />
        <br />
        <br />
        <Form.Label>Secondary Object: </Form.Label>
        <br />
        <SingleSelector
          objectList={secondaryObjectList}
          onChangeCurrentSelectedObject={onChangeCurrentSecondaryObject}
        />
        <br />
        <Button
          variant="primary"
          onClick={() => {
            otherActive
              ? onChangeOtherActive(false)
              : onChangeOtherActive(true);
          }}
        >
          Other
        </Button>
        <br />
        {otherActive ? (
          <OtherSecondaryForm
            onChangeCurrentSecondaryObject={onChangeCurrentSecondaryObject}
          />
        ) : null}
        <br />
      </Form.Group>
    </div>
  );
}

export { ObjectSelector };
