/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React, { Component } from "react";
import Form from "react-bootstrap/Form";

function InteractionDescription({ description, onChangeDescription }) {
  return (
    <Form>
      <Form.Group controlId="exampleForm.ControlTextarea1">
        <Form.Label>Action Description (Second Person):</Form.Label>
        <br />
        <Form.Control
          style={{ width: "500px", height: "80px" }}
          as="textarea"
          rows={3}
          placeholder="Describe the interaction between these two objects (Remember to commit to the medieval fantasy setting) - Start with 'You...'"
          onChange={(e) => onChangeDescription(e.target.value)}
        />
      </Form.Group>
    </Form>
  );
}

export { InteractionDescription };
