import React, {useEffect, useState} from "react";
import "./styles.css";
//BOOTSTRAP COMPONENTS

//CUSTOM COMPONENTS
import Header from "../../components/Header";
import MultipleChoice from "../../components/Questions/MultipleChoice";



const Task = ({
  data
})=> {
/*------------------------------------STATE------------------------------------*/
  //Selection Recieved from Backend.
  const [selectionData, setSelectionData]= useState([]);
  //Data that will be sent in Payload
  const [payloadData, setPayloadData]= useState([]);

  /*------------------------------------LIFE CYCLE------------------------------------*/
  //
  useEffect(()=>{
    let initialPayload = {}
    let initialSelectionData = Object.keys(data).map(selectionId=>{
      initialPayload.selectionId = {id:selectionId, sentence:data[selectionId], safety:null, context:null}
      return {id:selectionId, sentence:data[selectionId]}
    })
    setPayloadData(initialPayload);
    setSelectionData(initialSelectionData);
  },[data])


  return (
      <div className="app-container" >
        <Header/>
        {
          selectionData.length ?
          selectionData.map((selection, index)=>{
            const {id, sentence} = selection;
            return(
              <div>

              </div>
            )
          })
          :
          null
        }
      </div>
  );
}

export default Task ;
