import React from "react";
import { Checkbox, Button, Intent } from "@blueprintjs/core";

function noop() {}

export default function SubmitForm({ onSubmit, useModel, uniqueId }) {
  const [finishedForm, setFinishedForm] = React.useState(false);
  const [finishedSurvey, setFinishedSurvey] = React.useState(false);

  const surveyLink = useModel
    ? "https://forms.gle/gSG8Acw1xjRj28MB7"
    : "https://forms.gle/sEnR4KdSCohgBpwn9";

  return (
    <div className="completion">
      <Checkbox
        checked={finishedForm}
        onChange={() => setFinishedForm(!finishedForm)}
      >
        <strong>
          I confirm that I have finished populating all the tiles above.
        </strong>
      </Checkbox>
      <Checkbox
        checked={finishedSurvey}
        onChange={() => setFinishedSurvey(!finishedSurvey)}
      >
        <strong>
          I confirm that I have filled out the{" "}
          <a target="_blank" href={surveyLink}>
            linked survey
          </a>{" "}
          and filled in the following id:{" "}
          <span className="highlight">{uniqueId}</span>.
        </strong>
      </Checkbox>
      <Button
        onClick={onSubmit || noop}
        intent={Intent.PRIMARY}
        disabled={!finishedForm || !finishedSurvey}
      >
        Complete
      </Button>
    </div>
  );
}
