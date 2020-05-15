import React from "react";
import { Radio, RadioGroup, Intent } from "@blueprintjs/core";
import { useHistory } from "react-router-dom";

import { post } from "../utils";
import ObjectForm, { emptyObjectForm } from "./forms/ObjectForm";
import CharacterForm, { emptyCharacterForm } from "./forms/CharacterForm";
import RoomForm, { emptyRoomForm } from "./forms/RoomForm";
import AppToaster from "./AppToaster";

function CreatePage({ location }) {
  const [formType, setFormType] = React.useState(
    location.state ? location.state.type : "object"
  );

  return (
    <div>
      <h2
        data-testid="header"
        className="bp3-heading"
        style={{ marginBottom: 15 }}
      >
        Create new entity
      </h2>
      <div className="bp3-text-large">
        <div style={{ display: "flex", marginBottom: 30 }}>
          <span style={{ marginRight: "20px" }}>Entity type:</span>
          <RadioGroup
            inline
            large
            onChange={e => {
              location.state = undefined;
              setFormType(e.target.value);
            }}
            selectedValue={formType}
          >
            <Radio data-testid="radio-object" label="Object" value="object" />
            <Radio
              data-testid="radio-character"
              label="Character"
              value="character"
            />
            <Radio data-testid="radio-room" label="Room" value="room" />
          </RadioGroup>
        </div>
        <CreateForm
          type={formType}
          initialInputs={location.state ? location.state.entity : undefined}
        />
      </div>
    </div>
  );
}

function CreateForm({ type, initialInputs }) {
  const history = useHistory();
  const submitEntity = async payload => {
    await post(`entities/${type}`, payload).then(() => {
      history.push("/");
    });
    AppToaster.show({
      intent: Intent.SUCCESS,
      message: "Successfully created entity"
    });
  };

  switch (type) {
    case "object":
      return (
        <ObjectForm
          type={type}
          initialInputs={initialInputs ? initialInputs : emptyObjectForm}
          handleSubmit={submitEntity}
        />
      );
    case "character":
      return (
        <CharacterForm
          type={type}
          initialInputs={initialInputs ? initialInputs : emptyCharacterForm}
          handleSubmit={submitEntity}
        />
      );
    case "room":
      return (
        <RoomForm
          type={type}
          initialInputs={initialInputs ? initialInputs : emptyRoomForm}
          handleSubmit={submitEntity}
        />
      );
    default:
      return "This entity cannot be created at the moment";
  }
}

export default CreatePage;
