/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

//REACT
import React, {useEffect, useState} from "react";
//STYLES
import "./styles.css";
//CUSTOM COMPONENTS
import Header from "../../components/Header";
import SelectionList from "../../components/SelectionList";
import QuestionBlock from "../../components/QuestionBlock";
import TaskButton from "../../components/TaskButton";
import SuccessBanner from "../../components/SuccessBanner";
import ErrorBanner from "../../components/ErrorBanner";
//COPY
import TaskCopy from "../../TaskCopy";
const {
  taskHeader,
  defaultQuestions,
  successMessage
} = TaskCopy;

const Task = ({
  data
})=> {
/*------------------------------------STATE------------------------------------*/
  //Selection Recieved from Backend.
  const [selectionData, setSelectionData]= useState([]);
  //Data that will be sent in Payload
  const [payloadData, setPayloadData]= useState(null);
  // Boolean value that determines when Success Banner renders
  const [showSuccess, setShowSuccess] = useState(false);
  // Boolean value that determines when Error Banner renders
  const [showError, setShowError] = useState(false);
  // Array of strings populated by incomplete steps found during task submission
  const [errorMessage, setErrorMessage] = useState([])

  /*------------------------------------LIFE CYCLE------------------------------------*/
  useEffect(()=>{
    let initialPayload = {}
    let initialSelectionData = Object.keys(data).map(selectionId=>{
      initialPayload[selectionId] = {id:selectionId, sentence:data[selectionId], safety:null, context:null}
      return {id:selectionId, sentence:data[selectionId]}
    })
    setPayloadData(initialPayload);
    setSelectionData(initialSelectionData);
  },[data])
  /*------------------------------------HANDLERS------------------------------------*/
  const updateHandler = (id, field, value)=>{
    let unupdatedValue = payloadData[id]
    let updatedValue = {...unupdatedValue, [field]:value}
    let updatedPayloadData = {...payloadData, [id]: updatedValue}
    setPayloadData(updatedPayloadData)
  }
  const submissionHandler = ()=>{
    let errorList =[];
    const submissionData = payloadData;
    Object.keys(submissionData).map(submissionKey=>{
      const submissionValue = submissionData[submissionKey]
      const {sentence}= submissionValue
      Object.keys(submissionValue).map(attrKey=>{
        const attrValue = submissionValue[attrKey]
        if(attrValue===null){
          errorList.push(`No scoring for ${attrKey} was given for "${sentence}."`)
        }
      })
    })
    console.log("submissionPayload:  ", submissionData)
    if(!errorList.length){
      setShowError(false);
      console.log("SUCCESSFULLY READY TO SUBMIT")
      setShowSuccess(true);
      //handleSubmit()
    }else{
      setErrorMessage(errorList);
      setShowError(true);
    }
  }
  return (
      <div className="app-container" >
        <Header
          headerText={taskHeader}
        />
        <SuccessBanner
          showSuccess={showSuccess}
          toggleShowSuccess={()=>setShowSuccess(!showSuccess)}
          successMessage={successMessage}
        />
        <ErrorBanner
          showError={showError}
          hideError={()=>setShowError(false)}
          errors={errorMessage}
        />
        {
          selectionData.length ?
          <div>
            <SelectionList
              selection={selectionData}
            />
            {
            selectionData.map((selection, index)=>{
              const {id, sentence} = selection;
              return(
                <QuestionBlock
                  key={index}
                  headerText={sentence}
                  defaultQuestions={defaultQuestions}
                  updateFunction={(field, value)=>updateHandler(id, field, value)}
                />
              )
            })
            }
          </div>
          :
          null
        }
        <div className="submit-container">
          <TaskButton
            name="Submit"
            isSelected={false}
            unselectedContainer="submission-button__container"
            unselectedText="submission-selectedbutton__text "
            selectFunction={submissionHandler}
          />
        </div>
      </div>
  );
}

export default Task ;
