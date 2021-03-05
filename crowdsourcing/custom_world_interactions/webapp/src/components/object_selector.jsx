
import React, { Component } from 'react';
import Button from 'react-bootstrap/Button';
import Form from 'react-bootstrap/Form';

function ObjectSelector({ objectList, currentSelectedObject, onChangeCurrentSelectedObject }) {
  const [showMenu, setShowMenu] = React.useState(false);

  const objects = [];
  for (const [index, object] of objectList.entries()) {
    objects.push(
      <option>{object}</option>
    )
  }

  return (
    <div className="menu">
      <Form.Group controlId="exampleForm.ControlSelect1">
        <Form.Label>Target Object: </Form.Label>
        <Form.Control as="select" onChange={(e) => { onChangeCurrentSelectedObject(e.target.value); }}>
          {objects}
        </Form.Control>
      </Form.Group>
    </div>
  )
}

export { ObjectSelector };
