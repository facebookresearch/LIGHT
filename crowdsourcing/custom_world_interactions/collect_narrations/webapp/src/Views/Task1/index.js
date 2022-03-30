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
import DescriptionForm from "./DescriptionForm";

const Task1 = ({
  actionDescription,
  rawAction,
  taskData,
  onSubmit,
  isOnboarding,
  onError,
  setPrimaryObject,
  setSecondaryObject,
  setActionDescription,
  setRawAction,
  setOtherActive,
  payload,
  active
})=> {
  const [primaryObjectList, setPrimaryObjectList] = useState([]);
  const [secondaryObjectList, setSecondaryObjectList] = useState([]);
  const [showError, setShowError] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);
  const [errorMessage, setErrorMessage] = useState([])

  const toggleShowSuccess = () => setShowSuccess(!showSuccess);
  const toggleShowError = () => setShowError(!showError);
console.log("TASK DATA:  ", taskData)

  const {primaryObject, secondaryObject} = payload;

  useEffect(()=>{
      setPrimaryObjectList(taskData["primary_object_list"]);
      setSecondaryObjectList(taskData["secondary_object_list"]);
  },[taskData])

  const primaryHandler = (selection)=>{
    setPrimaryObject(selection)
  }

  const secondaryHandler = (selection)=>{
    setSecondaryObject(selection)
  }

  const otherHandler = (selection)=>{
    setOtherActive={selection}

  }
  const clearHandler = () =>{
    setPrimaryObject("");
    setSecondaryObject("");
    setActionDescription("");
  }
  const submitHandler = ()=>{
    if(active){
    onSubmit(payload);
    clearHandler()
    }else{
      let ErrorMessage = `${primaryObject ? "": "Must select a primary object"}${secondaryObject ? "": ",Must select a secondary Object"}${actionDescription ? "": ",Action description cannot be blank"}`.split(",")
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
          (primaryObjectList.length && secondaryObjectList.length) ?
          <div className="object-selectors">
            <ObjectSelector label="Primary Object" items={[...primaryObjectList]} selectFunction={primaryHandler} />
            <ObjectSelector label="Secondary Object" items={[...secondaryObjectList]} selectFunction={secondaryHandler} />
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
          placeholder={"In simple terms state the action between the two objects, e.g. swing axe at tree"}
          taskTemplate={"The action phrase should involve you using {primaryText} with {secondaryText}:"}
          tips={false}
        />
        <DescriptionForm
          formVal={actionDescription}
          formFunction={setActionDescription}
          primaryObject={primaryObject}
          secondaryObject={secondaryObject}
          name={"Description"}
          placeholder={"Describe the interaction between these two objects (Remember to commit to the medieval fantasy setting) - Start with 'You...'"}
          taskTemplate={"Your action should describe you using {primaryText} with {secondaryText}:"}
          tips={true}
        />
        {
          active
          ?
          <div
            className="submit-button"
            onClick={submitHandler}>
              SUBMIT
          </div>
          :
          <div
            disabled
            className="submit-button"
            onClick={submitHandler}>
              SUBMIT
          </div>
        }
      </div>
    </div>
  );
}

export default Task1 ;
