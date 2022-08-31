
/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

//REACT
import React, { useEffect, useState,useRef } from "react";
//STYLING
import "./styles.css";
//CUSTOM COMPONENTS
import Header from "../../components/Header";
import ScaleQuestion from "../../components/Questions/ScaleQuestion";
import AttributeQuestions from "./AttributeQuestions";
import TagQuestion from "../../components/Questions/TagQuestion";
import SelectionList from "../../components/SelectionList";
import TaskButton from "../../components/TaskButton";
import SuccessBanner from "../../components/SuccessBanner";
import ErrorBanner from "../../components/ErrorBanner";
//COPY
import TaskCopy from "../../TaskCopy";

//Task - Renders component that contains all questionns relevant to task.
const Task = ({
  data,//selection data retrieved from backend
  handleSubmit,//function that submits payload to backend
}) => {
  //COPY
  const {
    objects,
    characters,
    locations,
    input,
    attributeQuestionHeader,
    successMessage
  } = TaskCopy;
  /*------------------------------------STATE------------------------------------*/
  //Selection Recieved from Backend.
  const [selectionData, setSelectionData]= useState([]);
  //  String that details type of item selection is composed of
  //  Will be either objects, characters, or locations
  const [selectionDataType, setSelectionDataType]= useState("");
  //  Array of objects detailing the traits being rated on scale questions
  //  Each Item type has it's own defined in the TaskCopy File.
  const [traits, setTraits]= useState([]);
  //  Array of objects containing default questions for each item type
  const [attributeQuestions, setAttributeQuestions] = useState([]);
  //  Array of default dropdown options for typeahead tokenizer
  const [booleanAttributeOptions, setBooleanAttributeOptions]= useState([]);
  // Payload for boolean Attributes
  const [booleanPayload, setBooleanPayload] = useState([]);
  // Payload for Scale Attribute ratings
  const [scaleAttributePayload, setScaleAttributePayload] = useState({});
  // Payload for custom Scale Attribute ratings and input
  const [customScaleAttributesPayload, setCustomScaleAttributesPayload] = useState([{name:"", description:"", vals:{} }, {name:"", description:"" }]);
  // Boolean value that determines when Success Banner renders
  const [showSuccess, setShowSuccess] = useState(false);
  // Boolean value that determines when Error Banner renders
  const [showError, setShowError] = useState(false);
  // Array of strings populated by incomplete steps found during task submission
  const [errorMessage, setErrorMessage] = useState([])

  /*------------------------------------LIFE CYCLE------------------------------------*/
  //useEffect will handle setting the datatype from the selection
  useEffect(()=>{
    const {itemCategory, selection} = data;
    setSelectionDataType(itemCategory)
    setSelectionData(selection)
    if(itemCategory==="objects"){
      let {defaultBooleanAttributeOptions, traits, defaultQuestions}= objects;
      setTraits(traits)
      setBooleanAttributeOptions(defaultBooleanAttributeOptions)
      setAttributeQuestions(defaultQuestions)
    }else if(itemCategory==="characters"){
      let {defaultBooleanAttributeOptions, traits, defaultQuestions}= characters;
      setTraits(traits)
      setBooleanAttributeOptions(defaultBooleanAttributeOptions)
      setAttributeQuestions(defaultQuestions)
    }else if(itemCategory==="locations"){
      let {defaultBooleanAttributeOptions, traits, defaultQuestions}= locations;
      setTraits(traits)
      setBooleanAttributeOptions(defaultBooleanAttributeOptions)
      setAttributeQuestions(defaultQuestions)
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
    let baseScaleAttributePayload = {};
    //Adds attributes' names as keys and trait object as value
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

  const {booleanAttributes, defaultScaleRange} = input

  /*------------------------------------HANDLERS------------------------------------*/
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
//defaultAttributeQuestionUpdateHandler
  const defaultAttributeQuestionUpdateHandler = (position, updateKey, updateValue)=>{
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
    let errorList =[];
    const submissionPayload = {
      nodes:booleanPayload,
      attributes: {...scaleAttributePayload, custom_attributes:customScaleAttributesPayload}
    }

    /*---------- SUBMISSION CHECKS ----------*/
    /*Scale Attributes Ratings*/
    const {attributes} = submissionPayload;
    Object.keys(attributes).forEach(attr=>{
    //CUSTOM ATTRIBUTE CHECK
      if(attr == "custom_attributes"){
        let customAttributes = attributes[attr];
        customAttributes.map((custAttr, index)=>{
          Object.keys(custAttr).forEach(custAttrField=>{
            if(custAttrField == "vals"){
              let customAttributeRatings = custAttr[custAttrField];
              selectionData.map(selection => {
                const {name} = selection ;
                if(!customAttributeRatings[name]){
                  errorList.push(`${name} missing custom attribute ${index+1} rating`)
                }
              })
            }else if(!custAttr[custAttrField]){
              errorList.push(`Custom Attribute ${index+1} missing ${custAttrField} `)
            }
          })
        })
      }else{
      //DEFAULT ATTRIBUTE CHECK
        let nodeRatings = attributes[attr];
        Object.keys(nodeRatings).forEach(node=>{
          if(!nodeRatings[node]){
            errorList.push(`${node} missing ${attr} rating`)
          }
      })
    }
  })
  //BOOLEAN ATTRIBUTE CHECK
  const {nodes} = submissionPayload;
  nodes.map(node=>{
    let {name, values} = node;
    let {custom} = values;
    if(custom !== undefined){
      let customAttributesCount = custom.length;
      if(customAttributesCount == undefined){
        errorList.push(`${name} requires at least 4 custom attributes`)
      }else if(customAttributesCount<4){
        let requiredAttributesNumber = 4 - customAttributesCount;
        errorList.push(`${name} requires ${requiredAttributesNumber} more attributes`)
      }
    }else{
      errorList.push(`${name} requires at least 4 custom attributes`)
    }
  })
    console.log("submissionPayload:  ", submissionPayload)
    if(!errorList.length){
      console.log("SUCCESSFULLY READY TO SUBMIT")
      setShowSuccess(true);
      //handleSubmit()
    }else{
      setErrorMessage(errorList);
      setShowError(true);
    }
  }
    return (
      <div className="task-container">
        <Header/>
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
      <div className="attributequestion-container">
        <h1 className="attributequestion-header">
          {attributeQuestionHeader}
        </h1>
        <AttributeQuestions
          selection={selectionData}
          defaultQuestions={attributeQuestions}
          updateFunction={defaultAttributeQuestionUpdateHandler}
        />
        <TagQuestion
          selection={selectionData}
          booleanAttributeOptions={booleanAttributeOptions}
          updateFunction={booleanAttributeUpdateHandler}
        />
      </div>
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
