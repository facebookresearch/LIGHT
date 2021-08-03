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
  handleSubmit,
}) => {
  //COPY
  const {
    objects,
    characters,
    locations,
    input,
    tagQuestionHeader
  } = TaskCopy;
  //STATE
  const [selectionData, setSelectionData]= useState([]);
  const [selectionDataType, setSelectionDataType]= useState("");
  const [traits, setTraits]= useState([]);
  const [booleanAttributes, setBooleanAttributes]= useState([]);
  const [booleanPayload, setBooleanPayload] = useState([]);
  const [scaleAttributePayload, setScaleAttributePayload] = useState({});

  const [customScaleAttributesPayload, setCustomScaleAttributesPayload] = useState([{name:"", description:"", vals:{} }, {name:"", description:"" }]);
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
    let booleanAttributeBaseValues = selection.map(item=>{
      let {name, attributes}=item;
      let valObj ={custom:[]}
      attributes.map(attr=>{
        let {name, value} =attr;
        valObj[name]=value
      })
      let booleanAttributeObj = {name:name, values:valObj}
      return booleanAttributeObj
    })
    setBooleanPayload(booleanAttributeBaseValues)
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

  //HANDLERS
  //scaleAttributeUpdateHandler - Updates payload state with rating generated by user for scale questions
  const scaleAttributeUpdateHandler=(
    attributeName, //The name of the attribute of the items being scored. The name will be a key in payload.
    itemName, //The name of the item being scored, which will be the key who's value is the score in the payload.
    update// The score itself which will be generated when user drags the corresponding flag onto the scale.
    )=>{
    console.log("DRAG UPDATE: ", update)
    console.log("attributeName: ", attributeName)
    console.log("itemName: ", itemName)
    let unupdatedAttributes = {...scaleAttributePayload}
    unupdatedAttributes[attributeName][itemName]=update
    let updatedAttributes= unupdatedAttributes
    console.log("updatedAttribute:  ", updatedAttributes)
    setScaleAttributePayload(updatedAttributes)
  }
    //customScaleAttributeUpdateHandler - Updates payload state with ratings and header inputs generated by user for scale questions
    const customScaleAttributeUpdateHandler=(position, fieldName, updateKey, updateValue)=>{
      let updatedCustomAttributes;
      let updatedCustomAttribute;
      let unupdatedCustomAttribute = customScaleAttributesPayload[position]
      console.log("CUSTOM DRAG UPDATE: ", updateValue)
      console.log("CUSTOM FIELD NAME: ", fieldName)
      if(fieldName=="vals"){
        let unupdatedRatingValues = unupdatedCustomAttribute.vals
        let updatedRatingValues = {...unupdatedRatingValues, [updateKey]:updateValue}
        unupdatedCustomAttribute.vals = updatedRatingValues;
        updatedCustomAttribute = unupdatedCustomAttribute
      }else{
        unupdatedCustomAttribute[fieldName] = updateValue
      }
      updatedCustomAttribute = unupdatedCustomAttribute
      console.log("CUSTOM ATTS:  ", customScaleAttributesPayload)
      updatedCustomAttributes = customScaleAttributesPayload.map((attr, index) =>{
        console.log("CUSTOM ATTR:  ", attr)
        if(index == position){
          return updatedCustomAttribute;
        }else{
          return attr;
        }
      })
      console.log("updatedAttribute:  ", updatedCustomAttributes)
      setCustomScaleAttributesPayload(updatedCustomAttributes)
    }
  //booleanAttributeUpdateHandler
  const booleanAttributeUpdateHandler=(position, update)=>{

    let unupdatedAttributes = booleanPayload
    unupdatedAttributes[position].values = update;
    let updatedAttributes = unupdatedAttributes
    console.log("BOOLEAN UPDATES TO PAYLOAD  ATTR:  ", updatedAttributes, )
    setBooleanPayload(updatedAttributes)
  }
  //numericAttributeHandler
  const numericAttributeHandler = (position, updateKey, updateValue)=>{
    let unupdatedAttributes = booleanPayload;
    let unupdatedValues = unupdatedAttributes[position].values;
    let updatedValues = {...unupdatedValues, [updateKey]:updateValue};
    unupdatedAttributes[position].values = updatedValues;
    let updatedAttributes = unupdatedAttributes;
    console.log("BOOLEAN UPDATES TO PAYLOAD  ATTR:  ", updatedAttributes, )
    setBooleanPayload(updatedAttributes)
  }

  //submissionHandler
  const submissionHandler=()=>{
    let submissionPayload = {
      nodes:booleanPayload,
      attributes: {...scaleAttributePayload, custom_attributes:customScaleAttributesPayload}
    }
    console.log("DUMMY DATA", selectionData)
    console.log("DATA TYPE", selectionDataType)
    console.log("ScaleAttributePayload :  ", scaleAttributePayload)
    console.log("BOOLEAN PAYLOAD:  ", booleanPayload)
    console.log("submissionPayload:  ", submissionPayload)

    //handleSubmit()
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
          let {name, scaleRange, requiredAttribute} = trait;
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
                  updateFunction={(selectionName, update)=>{scaleAttributeUpdateHandler(name, selectionName, update )}}
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
              updateFunction={(selectionName, update)=>{scaleAttributeUpdateHandler(name, selectionName, update )}}
            />
          )}
        })
        :
        null
      }
      {
        customScaleAttributesPayload ?
        customScaleAttributesPayload.map((trait, index)=>{

          return(
            <ScaleQuestion
              key={index}
              id={index}
              scaleRange={defaultScaleRange}
              selection={selectionData}
              trait={trait}
              isCustom={true}
              updateFunction={(fieldName,  updateKey, updateValue)=>{customScaleAttributeUpdateHandler(index, fieldName, updateKey, updateValue)}}
            />
          )
        })
        :null
      }
        <TagQuestion
          header={tagQuestionHeader}
          selection={selectionData}
          booleanAttributes={booleanAttributes}
          updateFunction={booleanAttributeUpdateHandler}
          numericAttributeUpdateFunction={numericAttributeHandler}
        />
        <TaskButton
          name="Submit"
          isSelected={false}
          unselectedContainer="submission-button__container"
          unselectedText="submission-selectedbutton__text "
          selectFunction={submissionHandler}
        />
      </div>
    );
}

export default Task ;
