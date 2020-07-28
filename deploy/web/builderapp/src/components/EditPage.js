import React from "react";
import { isEmpty } from "lodash";
import { Button, Classes, Dialog, Intent, Spinner } from "@blueprintjs/core";
import { useHistory } from "react-router-dom";

import CONFIG from "../config";
import { useAPI, post } from "../utils";
import ObjectForm from "./forms/ObjectForm";
import CharacterForm from "./forms/CharacterForm";
import RoomForm from "./forms/RoomForm";
import AppToaster from "./AppToaster";

function EditPage({ match, location }) {
  const [formType, setFormType] = React.useState(undefined);
  const { loading, result } = useAPI(
    CONFIG,
    `/entities/${match.params.id}`,
    {},
    location.state
  );
  const [initialInputs, setInitialInputs] = React.useState({});
  const [showDialog, setShowDialog] = React.useState(false);
  const [pendingEdits, setPendingEdits] = React.useState([]);
  const history = useHistory();

  if (!loading && isEmpty(initialInputs)) {
    if (isEmpty(result) || isEmpty(result.entity)) {
      setInitialInputs({ id: match.params.id });
      setFormType("invalid");
    } else {
      setInitialInputs(result.entity);
      setFormType(result.type);
    }
  }

  const showEdits = (values) => {
    const edits = [];
    for (let property in values) {
      if (values[property] !== initialInputs[property]) {
        edits.push({ property: property, editedValue: values[property] });
      }
    }
    setPendingEdits(edits);
    setShowDialog(true);
  };

  return (
    <div>
      <Dialog
        icon="info-sign"
        onClose={() => setShowDialog(false)}
        title={`Confirm edits for Entity ${match.params.id}`}
        isOpen={showDialog}
        usePortal={false}
      >
        <div className={Classes.DIALOG_BODY}>
          {pendingEdits.map((edit, index) => {
            return (
              <p key={index}>
                <strong>{edit.property}</strong>: {edit.editedValue.toString()}
              </p>
            );
          })}
        </div>
        <div className={Classes.DIALOG_FOOTER}>
          <div className={Classes.DIALOG_FOOTER_ACTIONS}>
            <Button onClick={() => setShowDialog(false)}>Close</Button>
            <Button
              intent={Intent.PRIMARY}
              onClick={() =>
                submitEdits(match.params.id, pendingEdits, history)
              }
            >
              Confirm Edits
            </Button>
          </div>
        </div>
      </Dialog>
      <h2 data-testid="header" className="bp3-heading">
        Editing Entity {match.params.id}
      </h2>
      <div className="bp3-text-large">
        {loading ? (
          <Spinner intent={Intent.PRIMARY} />
        ) : (
          <EditForm
            type={formType}
            initialInputs={initialInputs}
            handleSubmit={showEdits}
          />
        )}
      </div>
    </div>
  );
}

function EditForm({ type, initialInputs, handleSubmit }) {
  switch (type) {
    case "object":
      return (
        <ObjectForm
          type={type}
          initialInputs={initialInputs}
          handleSubmit={handleSubmit}
        />
      );
    case "character":
      return (
        <CharacterForm
          type={type}
          initialInputs={initialInputs}
          handleSubmit={handleSubmit}
        />
      );
    case "room":
      return (
        <RoomForm
          type={type}
          initialInputs={initialInputs}
          handleSubmit={handleSubmit}
        />
      );
    default:
      return "This entity cannot be edited at the moment";
  }
}

async function submitEdits(id, edits, history) {
  const reqs = edits.map((edit) =>
    submitEdit(id, edit.property, edit.editedValue)
  );
  await Promise.all(reqs).then(() => {
    history.push("/");
  });
  AppToaster.show({
    intent: Intent.SUCCESS,
    message: "Successfully created edits",
  });
}

function submitEdit(id, field, edited_value) {
  const payload = {
    id,
    field,
    edited_value,
    player: 1,
  };

  return post("builder/edits", payload);
}

export default EditPage;
