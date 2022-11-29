import React, {useEffect, useState} from "react";
import "./styles.css";
//BOOTSTRAP COMPONENTS
import Toast from 'react-bootstrap/Toast';
import ToastHeader from 'react-bootstrap/ToastHeader';
import ToastBody from 'react-bootstrap/ToastBody';
import { BsExclamationOctagonFill, BsCheck, BsX } from "react-icons/bs";
//CUSTOM COMPONENTS
import CollapsibleContainer from "../../components/CollapsibleContainer";
import TaskDescription from "../../components/TaskDescription";
import ObjectSelector from "../../components/ObjectSelector";
import ObjectDescriber from "../../components/ObjectDescriber";
import DescriptionForm from "./DescriptionForm";

const Copy = {
  basic: {
    rawActionDescription: "In simple terms state the action between the two objects, e.g. swing axe at tree, wipe mirror with cloth",
    rawActionTemplate: "The action phrase should involve using {primaryText} with {secondaryText}:",
    narrationDescription: "Describe the interaction between these two objects (Remember to commit to the medieval fantasy setting) - Start with 'You...', e.g. You swing the axe, easily felling the tree and releasing shards of bark everywhere.",
    narrationTemplate: "Your action should describe you using {primaryText} with {secondaryText}:",
  },
  boring: {
    rawActionDescription: "In simple terms state the action between the two objects, e.g. hit rock with spoon, bounce ball off wall",
    rawActionTemplate: "The action phrase should involve using {primaryText} with {secondaryText}:",
    narrationDescription: "Describe the interaction between these two objects (Remember to commit to the medieval fantasy setting) - Start with 'You...', e.g. You hit the rock with the spoon, and it makes a satisfying 'dink' sound.",
    narrationTemplate: "Your action should describe you using {primaryText} with {secondaryText}, and the action shouldn't change the final location/position, description, or attributes of the objects:",
  },
  failing: {
    rawActionDescription: "In simple terms state an action between the two objects THAT SHOULDN'T BE POSSIBLE or DON'T MAKE SENSE, e.g. ignite river with match, unlock apple with key",
    rawActionTemplate: "The action phrase should involve using {primaryText} with {secondaryText}, but the action should be impossible:",
    narrationDescription: "Describe the failure of the interaction between the two objects such that the actor doesn't act or neither object is modified. (Remember to commit to the medieval fantasy setting) - Start with 'You...', e.g. You can't ignite a river! All you'd be left with is a soaked matchstick.",
    narrationTemplate: "Your action should describe you attempting and failing to use {primaryText} with {secondaryText}, or not being able to do the given action for some reason:",
  },
}

const Task1 = ({
  taskData,
  onSubmit,
  isOnboarding,
  onError,
  setPrimaryObject,
  setPrimaryDescription,
  setSecondaryObject,
  setActionDescription,
  setRawAction,
  payload,
  active
}) => {
  const [secondaryObjectList, setSecondaryObjectList] = useState([]);
  const [showError, setShowError] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);
  const [errorMessage, setErrorMessage] = useState([])

  const toggleShowSuccess = () => setShowSuccess(!showSuccess);
  const toggleShowError = () => setShowError(!showError);
  const {primaryObject, secondaryObject, primaryDescription, actionDescription, rawAction} = payload;
  const copy = Copy.failing;

  useEffect(()=>{
      setSecondaryObjectList(taskData["secondary_object_list"]);
  }, [taskData])

  const submitHandler = ()=>{
    if (active) {
      onSubmit(payload);
    } else {
      let ErrorMessage = `${primaryObject ? "": "Must create a primary object"}${primaryDescription ? "": ",Must describe the primary object"}${secondaryObject ? "": ",Must select a secondary Object"}${actionDescription ? "": ",Action description cannot be blank"}`.split(",")
      console.log(ErrorMessage)
      setErrorMessage(ErrorMessage)
      setShowError(true)
    }
  }

  return (
    <div className="app-container" >
      <div className="header">
        <h1 className="header__text">Object Interaction Narrations</h1>
      </div>
      <>
        <Toast show={showError} onClose={toggleShowError} style={{backgroundColor:"red"}} delay={3000} autohide >
          <Toast.Header closeButton={false} style={{backgroundColor:"red", color:"white",textDecoration:"underline", textDecorationColor:"white", display:"flex", justifyContent:"space-between", alignItems:"center", paddingLeft:'2em'}}>
            <span style={{display:"flex", justifyContent:"center", alignItems:"center"}}>
              <BsExclamationOctagonFill color="white" style={{fontSize:"18px"}}/>
              <strong className="mr-auto" style={{color:"white", fontWeight:"bold", marginLeft:"5px"}}>ERROR</strong>
            </span>
            <BsX color="white" onClick={toggleShowError} style={{fontSize:"18px"}} />
          </Toast.Header>
          <Toast.Body style={{fontSize:"18px", color:"white", paddingLeft:'4em'}}>
            <ul>
              {
              errorMessage.map((err, id)=>{
                if(err !== undefined && err.length){
                  return <li key={id}>{err}</li>
                  }
                })
              }
            </ul>
            </Toast.Body>
        </Toast>
        <Toast show={showSuccess} onClose={toggleShowSuccess} delay={3000} autohide >
          <Toast.Header closeButton={false} style={{backgroundColor:"green", color:"white"}}>
            <BsCheck color="white" style={{fontSize:"18px"}}/>
            <strong className="mr-auto">SUCCESS</strong>
            <BsX color="white" onClick={toggleShowSuccess} style={{fontSize:"18px"}}/>
          </Toast.Header>
          <Toast.Body>You have successfully completed task</Toast.Body>
        </Toast>
      </>
      <div className="task-container">
        <CollapsibleContainer
          title="INSTRUCTIONS"
        >
          <TaskDescription/>
        </CollapsibleContainer>
        {
          (secondaryObjectList.length) ?
          <div className="object-selectors">
            <ObjectSelector
              label={"Secondary Item:"}
              items={[...secondaryObjectList]}
              selectedItem={secondaryObject}
              selectFunction={(obj) => setSecondaryObject(obj)}
            />
            <ObjectDescriber
              name={primaryObject}
              description={primaryDescription}
              onChangeName={setPrimaryObject}
              onChangeDescription={setPrimaryDescription}
            />
          </div>
          :
          <div/>
        }
        <DescriptionForm
          formVal={rawAction}
          formFunction={setRawAction}
          primaryObject={primaryObject}
          secondaryObject={secondaryObject}
          name={"Action Phrase"}
          placeholder={copy.rawActionDescription}
          taskTemplate={copy.rawActionTemplate}
          tips={false}
          bigForm={false}
        />
        <DescriptionForm
          formVal={actionDescription}
          formFunction={setActionDescription}
          primaryObject={primaryObject}
          secondaryObject={secondaryObject}
          name={"Description"}
          placeholder={copy.narrationDescription}
          taskTemplate={copy.narrationTemplate}
          tips={true}
          bigForm={true}
        />
        <button
          className="submit-button"
          onClick={submitHandler}
          disabled={!active}>
            SUBMIT
        </button>
      </div>
    </div>
  );
}

export default Task1 ;
