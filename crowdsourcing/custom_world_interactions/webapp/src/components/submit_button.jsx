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
