//REACT
import React, {useEffect, useState} from "react";
//STYLES
import "./styles.css";
//CUSTOM COMPONENTS
import Header from "../../components/Header";
import QuestionBlock from "../../components/QuestionBlock";
//COPY
import TaskCopy from "../../TaskCopy";
const {taskHeader, defaultQuestions} = TaskCopy

const Task = ({
  data
})=> {
/*------------------------------------STATE------------------------------------*/
  //Selection Recieved from Backend.
  const [selectionData, setSelectionData]= useState([]);
  //Data that will be sent in Payload
  const [payloadData, setPayloadData]= useState([]);

  /*------------------------------------LIFE CYCLE------------------------------------*/
  useEffect(()=>{
    let initialPayload = {}
    let initialSelectionData = Object.keys(data).map(selectionId=>{
      initialPayload.selectionId = {id:selectionId, sentence:data[selectionId], safety:null, context:null}
      return {id:selectionId, sentence:data[selectionId]}
    })
    setPayloadData(initialPayload);
    setSelectionData(initialSelectionData);
  },[data])
  /*------------------------------------HANDLERS------------------------------------*/
  const UpdateHandler = (id, field, value)=>{
    let unupdatedValue = payloadData[id]
    let updatededValue = {...unupdatedValue, [field]:value}
    let updatedPayloadData = {...payloadData, [id]: updatededValue}
    setPayloadData(updatedPayloadData)
  }
  return (
      <div className="app-container" >
        <Header
          headerText={taskHeader}
        />
        <div>
        {
          selectionData.length ?
          selectionData.map((selection, index)=>{
            const {id, sentence} = selection;
            return(
              <QuestionBlock
                key={id}
                headerText={sentence}
                selectionNode={selection}
                defaultQuestions={defaultQuestions}
                updateFunction={(field, value)=>UpdateHandler(id, field, value)}
              />
            )
          })
          :
          null
        }
        </div>
      </div>
  );
}

export default Task ;
