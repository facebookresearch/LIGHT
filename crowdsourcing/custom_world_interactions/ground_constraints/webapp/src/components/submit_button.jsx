/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React, { Component } from "react";
import Button from "react-bootstrap/Button";

function SubmitButton({ active, state, onSubmit }) {
  if (active) {
    return (
      <div>
        <p>
          <b>Warning:</b> Please make sure ONLY the two objects are involved in
          your action.
        </p>
        <Button
          variant="primary"
          onClick={() => {
            onSubmit(state);
          }}
        >
          Submit
        </Button>
      </div>
    );
  } else {
    return (
      <Button variant="secondary" disabled>
        Submit
      </Button>
    );
  }
}

export { SubmitButton };
