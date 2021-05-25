import React, {useEffect, useState} from "react";
import "./styles.css";
//BOOTSTRAP COMPONENTS
import Toast from 'react-bootstrap/Toast';
import ToastHeader from 'react-bootstrap/ToastHeader';
import ToastBody from 'react-bootstrap/ToastBody';
//CUSTOM COMPONENTS
import CollapsibleContainer from "../../components/CollapsibleContainer";
import TaskDescription from "../../components/TaskDescription";
import ObjectSelector from "../../components/ObjectSelector";
import DescriptionForm from "./DescriptionForm";

const Task1 = ({
  actionDescription,
  taskData,
  onSubmit,
  isOnboarding,
  onError,
  setPrimaryObject,
  setSecondaryObject,
  setActionDescription,
  setOtherActive,
  payload,
  active
})=> {
  const [primaryObjectList, setPrimaryObjectList] = useState([]);
  const [secondaryObjectList, setSecondaryObjectList] = useState([]);
  const [showError, setShowError] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);
  const [errorMessage, setErrorMessage]

  const toggleShowSuccess = () => setShowSuccess(!showSuccess);
  const toggleShowError = () => setShowError(!showError);



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

  const descHandler = (selection)=>{
    setOtherActive={selection}

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
      let {primaryObject, secondaryObject} = payload;
      let ErrorMessage = `${primaryObject ? "": "Must select a primary object"} ${secondaryObject ? "": "Must select a secondary Object"} ${actionDescription ? "": "Action description cannot be blank"}`
      setError(ErrorMessage)
      setShowError(true)
    }
  }

  return (
    <div className="app-container" >
      <div className="header">
        <h1 className="header__text">Object Interaction Narrations</h1>
      </div>
      <>
        <Toast show={showError} onClose={toggleShowError}>
          <Toast.Header style={{backgroundColor:"red", color:"white"}}>
            <img src="holder.js/20x20?text=%20" className="rounded mr-2" alt="" />
            <strong className="mr-auto">Bootstrap</strong>
            <small>just now</small>
          </Toast.Header>
          <Toast.Body>See? Just like this.</Toast.Body>
        </Toast>
        <Toast show={showSuccess} onClose={toggleShowSuccess} >
          <Toast.Header>
            <img src="holder.js/20x20?text=%20" className="rounded mr-2" alt="" />
            <strong className="mr-auto">Bootstrap</strong>
            <small>2 seconds ago</small>
          </Toast.Header>
          <Toast.Body>Heads up, toasts will stack automatically</Toast.Body>
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
            <ObjectSelector label="Primary Object" items={primaryObjectList} selectFunction={primaryHandler} />
            <ObjectSelector label="Secondary Object" items={secondaryObjectList} selectFunction={secondaryHandler} />
          </div>
          :
          <div/>
        }
        <DescriptionForm formVal={actionDescription} formFunction={setActionDescription} />
        <div
          disabled={!active}
          className="submit-button"
          onClick={submitHandler}>
          SUBMIT
        </div>
      </div>
    </div>
  );
}

export default Task1 ;
