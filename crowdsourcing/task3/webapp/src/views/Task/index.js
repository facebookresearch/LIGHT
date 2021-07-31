//REACT
import React, { useEffect, useState,useRef } from "react";
//STYLING
import "./styles.css"
//CUSTOM COMPONENTS
import Header from "../../components/Header";
import ScaleQuestion from "../../components/Questions/ScaleQuestion";
import TagQuestion from "../../components/Questions/TagQuestion";
import SelectionList from "../../components/SelectionList";
import TaskButton from "../../components/TaskButton"
//COPY
import TaskCopy from "../../TaskCopy";

//Task - Renders component that contains all questionns relevant to task.
const Task = ({
  data,
  submissionHandler,
}) => {
  //COPY
  const {objects, characters, locations, input, tagQuestionHeader} = TaskCopy;
  //STATE
  const [selectionData, setSelectionData]= useState([]);
  const [selectionDataType, setSelectionDataType]= useState("");
  const [traits, setTraits]= useState([]);
  const [booleanAttributes, setBooleanAttributes]= useState([]);
  const [booleanPayload, setBooleanPayload] = useState([])
  const [scaleAttributePayload, setScaleAttributePayload] = useState({})
  const [customAttributePayload, setCustomAttributePayload] = useState([])
  //useEffect will handle data type
  useEffect(()=>{
    const {itemCategory, selection} = data;
    setSelectionDataType(itemCategory)
    setSelectionData(selection)
    if(itemCategory==="objects"){
      let {booleanAttributes, traits}= objects;
      setTraits(traits)
      setBooleanAttributes(booleanAttributes)
    }else if(itemCategory==="characters"){
      let {booleanAttributes, traits}= characters;
      setTraits(traits)
      setBooleanAttributes(booleanAttributes)
    }else if(itemCategory==="locations"){
      let {booleanAttributes, traits}= locations;
      setTraits(traits)
      setBooleanAttributes(booleanAttributes)
    }
  },[data])

  useEffect(()=>{
    let baseScaleAttributePayload = {}
    //Adds attributes' names as keys and trait object as value
    console.log("TRAITS IN USE EFFECT :  ", traits)
    traits.map((trait, index)=>{
      let scaleAttributeBaseValues = {}
      let filteredSelection = selectionData;
      if(trait.requiredAttribute){
        let {requiredAttribute} = trait;
        filteredSelection = selectionData.filter(item=>{
          let {attributes}=item;
          return attributes.filter(attribute => attribute.name == requiredAttribute).length
        })
      }
      //Adds selection names as keys without values as value to attribute
      filteredSelection.map((selection,index)=>{
        let {name}=selection
        scaleAttributeBaseValues = {...scaleAttributeBaseValues, [name]:null}
      })
      baseScaleAttributePayload[trait.name]=scaleAttributeBaseValues
    })
    setScaleAttributePayload(baseScaleAttributePayload)
  }, [traits])
  console.log("DUMMY DATA", selectionData)
  console.log("DATA TYPE", selectionDataType)
  console.log("TRAITS", traits)
  console.log("ScaleAttributePayload :  ", scaleAttributePayload)
  const {defaultBooleanAttributes, defaultScaleRange} = input
  const clickHandler=()=>{
    console.log("DUMMY DATA", selectionData)
    console.log("DATA TYPE", selectionDataType)
    console.log("ScaleAttributePayload :  ", scaleAttributePayload)
  }
    return (
      <div className="task-container">
        <Header/>
      {
        data.length ?
        <SelectionList selection={selectionData} />
        :
        null
      }
      {
        traits.length
        ?
        traits.map((trait, index)=>{
          let {scaleRange, requiredAttribute} = trait;
          if(requiredAttribute){
            let filteredSelection = selectionData.filter(item =>{
              let {attributes} = item;
              let matchedAttributes = attributes.filter(attr=>(attr.name==requiredAttribute));
              let hasAttribute = !!matchedAttributes.length;
              return hasAttribute
            } )
            if(!filteredSelection.length){
              return null;
            }
            if(filteredSelection.length){
              return (
                <ScaleQuestion
                  key={index}
                  scaleRange={scaleRange}
                  selection={filteredSelection}
                  trait={trait}
                  isInputHeader={false}
                />
              )
            }
          }else{
          return(
            <ScaleQuestion
              key={index}
              scaleRange={scaleRange}
              selection={selectionData}
              trait={trait}
              isInputHeader={false}
            />
          )}
        })
        :
        null
      }
        <ScaleQuestion
          scaleRange={defaultScaleRange}
          selection={selectionData}
          trait={"trait"}
          isInputHeader={true}
        />
        <ScaleQuestion
          scaleRange={defaultScaleRange}
          selection={selectionData}
          trait={"trait"}
          isInputHeader={true}
        />
        <TagQuestion
          header={tagQuestionHeader}
          selection={selectionData}
          booleanAttributes={booleanAttributes}
        />
        <TaskButton
          name="Submit"
          isSelected={false}
          unselectedContainer="submission-button__container"
          unselectedText="submission-selectedbutton__text "
          selectFunction={clickHandler}
        />
      </div>
    );
}

export default Task ;


// {
//   'nodes': [
//       'node1': {
//           'boolean-numeric-attribute1': value,
//            .... rest of boolean/numeric attributes....
//       },
//       ... rest of provided nodes ....
//   ],
//   'attributes': {
//       'scaled_attribute_1': {'obj1': val, ...},
//       'custom_attributes': [
//           {'name': attribute name, 'vals': {'objx': val, ...}},
//           ...
//       ],
//   },
// }
