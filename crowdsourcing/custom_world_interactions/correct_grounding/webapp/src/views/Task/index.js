//REACT
import React, { useEffect, useState} from "react";
//STYLING
import "./styles.css"
//Custom Components
import Header from "../../components/Header";
import TaskDataCards from "./TaskDataCards"
import Submission from "../../components/Submission";
import ErrorToast from "../../components/ErrorToast";
import NarrationEditor from "../../components/NarrationEditor";
import ObjectsEditor from "../../components/ObjectsEditor";
import AttributesEditor from "../../components/AttributesEditor";

}

function getAttributeDictBaseVal(attributeDict) {
  let retDict = {};
  for (item in attributeDict) {
    let retItemDict = {};
    for (attribute in attributeDict[item]) {
      retItemDict[attribute] = "";
    }
    retItemDict['EXTRAS'] = "";
    retDict[item] = retItemDict
  }
  return retDict;
}


//Task - Primary View for task, contains the Header, both the events and constraints, and the Task Cards.
const Task = ({
  data,
  handleSubmit,
}) => {
  // Task state
  //// Error Handling
  const [showError, setShowError] = useState(false);
  const [errorMessages, setErrorMessages] = useState([]);
  //// Validation
  const [interactionValid, setInteractionValid] = useState(true);
  const [primaryItem, setPrimaryItem] = useState("");
  //// Narration
  const [usesExternalContext, setUsesExternalContext] = useState(false);
  const [updatedNarration, setUpdatedNarration] = useState("");
  const [externalPerspective, setExternalPerspective] = useState(data.external_perspective);
  //// Objects after
  const [remainingObjects, setRemainingObjects] = useState(data.objects_afterwards);
  const [finalDescriptions, setFinalDescriptions] = useState(data.descriptions_afterwards);
  const [finalLocations, setFinalLocations] = useState(data.locations_afterwards);
  //// Attributes
  const [beforeAttributes, setBeforeAttributes] = useState(getAttributeDictBaseVal(data.object_attributes.before));
  const [afterAttributes, setAfterAttributes] = useState(getAttributeDictBaseVal(data.object_attributes.after));

  const payload = {
    interactionValid,
    usesExternalContext,
    updatedNarration,
    narrationRanges,
    primaryItem,
    externalPerspective,
    remainingObjects,
    finalDescriptions,
    finalLocations,
    beforeAttributes,
    afterAttributes,
  }

  function submissionHandler() {
    // Do some checking first
    if (true) {
      setErrorMessages("hello");
      setShowError(true);
    } else {
      handleSubmit(payload);
    }
  }

  return (
    <div className="view-container">
      <ErrorToast errors={errorMessages} showError={showError} hideError={() => setShowError(false)} />
      <Header/>
      <TaskDataCards
        object1={data.primary}
        object1_desc={data.primary_desc}
        object2={data.secondary}
        object2_desc={data.secondary_desc}
        rawAction={data.raw_action}
        interaction={data.action_desc}
        primaryItem={primaryItem}
        setPrimaryItem={setPrimaryItem}
        interactionValid={interactionValid}
        setInteractionValid={setInteractionValid}
      />
      <div className="task-container">
        <NarrationEditor
          usesExternalContext={usesExternalContext}
          setUsesExternalContext={setUsesExternalContext}
          updatedNarration={updatedNarration}
          setUpdatedNarration={setUpdatedNarration}
          externalPerspective={externalPerspective}
          setExternalPerspective={setExternalPerspective}
        />
        <ObjectsEditor
          remainingObjects={remainingObjects}
          setRemainingObjects={setRemainingObjects}
          finalDescriptions={finalDescriptions}
          setFinalDescriptions={setFinalDescriptions}
          finalLocations={finalLocations}
          setFinalLocations={setFinalLocations}
          afterAttributes={afterAttributes}
          setAfterAttributes={setAfterAttributes}
        />
        <AttributesEditor
          beforeAttributes={beforeAttributes}
          setBeforeAttributes={setBeforeAttributes}
          afterAttributes={afterAttributes}
          setAfterAttributes={setAfterAttributes}
        /> {/* TODO make list editor, and multi-list selector */}
      </div>
      <div>
        <Submission
          submitFunction={() => submissionHandler}
        />
      </div>
    </div>
  );
}

export default Task ;
