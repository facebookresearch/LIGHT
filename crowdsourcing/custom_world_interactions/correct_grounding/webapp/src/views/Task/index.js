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

function getAttributeDictBaseVal(attributeDict) {
  let retDict = {};
  for (let item in attributeDict) {
    let retItemDict = {};
    for (let attribute in attributeDict[item]) {
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
  const [primaryItem, setPrimaryItem] = useState(null);
  //// Narration
  const [usesExternalContext, setUsesExternalContext] = useState(null);
  const [updatedNarration, setUpdatedNarration] = useState(data.action_desc);
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
    let errors = [];
    if (primaryItem === null) {
      errors.push("Be sure to pick a primary item for question 2. ");
    }
    if (usesExternalContext === null) {
      errors.push("Annotate whether or not this interaction uses external context in question 3. ");
    }
    if (updatedNarration === data.action_desc) {
      errors.push("You must provide a modified interaction description in question 4. ");
    } 
    if (Object.entries(finalDescriptions).filter(([_, x]) => x.length == 0).length != 0) {
      errors.push("Be sure to provide a description for each object present after the interaction in question 7. ");
    }
    if (Object.entries(finalLocations).filter(([_, x]) => x.length == 0).length != 0) {
      errors.push("Be sure to provide a final location for each object present after the interaction in question 8. ");
    }
    for (let itemName in beforeAttributes) {
      if (Object.entries(beforeAttributes[itemName]).filter(([att_name, reason]) => (att_name != 'EXTRAS' && reason.length == 0)).length != 0) {
        errors.push("Be sure to provide an answer for whether or not each attribute in question 9 is required before the interaction and why. ");
        break;
      }
    }
    for (let itemName in afterAttributes) {
      if (Object.entries(afterAttributes[itemName]).filter(([att_name, reason]) => (att_name != 'EXTRAS' && reason.length == 0)).length != 0) {
        errors.push("Be sure to provide an answer for whether or not each attribute in question 10 is required after the interaction and why.");
        break;
      }
    }
    if (errors.length > 0) {
      setErrorMessages(errors);
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
          interaction={data.action_desc}
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
        />
      </div>
      <div>
        <Submission
          submitFunction={() => submissionHandler()}
        />
      </div>
    </div>
  );
}

export default Task ;
