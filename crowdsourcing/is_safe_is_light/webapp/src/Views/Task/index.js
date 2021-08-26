import React, {useEffect, useState} from "react";
import "./styles.css";
//BOOTSTRAP COMPONENTS

//CUSTOM COMPONENTS
import Header from "../../components";



const Task = ({

})=> {
/*------------------------------------STATE------------------------------------*/
  //Selection Recieved from Backend.
  const [selectionData, setSelectionData]= useState([]);
  //Data that will be sent in Payload
  const [payloadData, setPayloadData]= useState([]);

  /*------------------------------------LIFE CYCLE------------------------------------*/
  //
  useEffect(()=>{
    const {selection} = data;
    let initialPayload = {}
    Object.keys(selection).forEach(selectionId=>{
      initialPayload.selectionId = {id:selectionId, sentence:selection[selectionId], safety:null, context:null}
    })
    setPayloadData(initialPayload)
  },[data])


  return (
      <div className="app-container" >
        <Header/>

      </div>
  );
}

export default Task ;
