//REACT
import React, { useEffect, useState } from "react";
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
  ObjectDummyData,
  CharacterDummyData,
  LocationDummyData
}) => {
  //COPY
  const {objects, characters, locations, input} = TaskCopy;
  //STATE
  const [data, setData]= useState(ObjectDummyData);
  const [dataType, setDataType]= useState("objects");
  const [traits, setTraits]= useState([]);
  const [booleanAttributes, setBooleanAttributes]= useState([]);
  //useEffect will handle data type
  useEffect(()=>{
    if(dataType==="objects"){
      setData(ObjectDummyData)
      let {booleanAttributes, traits}= objects;
      setTraits(traits)
      setBooleanAttributes(booleanAttributes)
    }else if(dataType==="characters"){
      setData(CharacterDummyData)
      let {booleanAttributes, traits}= characters;
      setTraits(traits)
      setBooleanAttributes(booleanAttributes)
    }else if(dataType==="locations"){
      setData(LocationDummyData)
      let {booleanAttributes, traits}= locations;
      setTraits(traits)
      setBooleanAttributes(booleanAttributes)
    }
  },[dataType])
  console.log("DUMMY DATA", data)
  console.log("DATA TYPE", dataType)
  console.log("TRAITS", traits)
  const {defaultBooleanAttributes, defaultScaleRange} = input
  const SelectObjects = ()=>setDataType("objects")
  const SelectCharacters = ()=>setDataType("characters")
  const SelectLocations = ()=>setDataType("locations")
    return (
      <div className="task-container">
        <Header/>
        <div style={{display:"flex", flexDirection:"row", width:"90%", margin:"15px" }}>
          <TaskButton
            name="Objects"
            isSelected={dataType==="objects"}
            selectFunction={SelectObjects}
            unselectedContainer="b-button__container"
            unselectedText="b-button__text"
            selectedContainer="b-selectedbutton__container true"
            selectedText="b-selectedbutton__text"
          />
          <TaskButton
            name="Characters"
            isSelected={dataType==="characters"}
            selectFunction={SelectCharacters}
            unselectedContainer="b-button__container"
            unselectedText="b-button__text"
            selectedContainer="b-selectedbutton__container true"
            selectedText="b-selectedbutton__text"
          />
          <TaskButton
            name="Locations"
            isSelected={dataType==="locations"}
            selectFunction={SelectLocations}
            unselectedContainer="b-button__container"
            unselectedText="b-button__text"
            selectedContainer="b-selectedbutton__container true"
            selectedText="b-selectedbutton__text"
          />
        </div>
      {
        data.length ?
        <SelectionList selection={data} />
        :
        null
      }
      {
        traits.length
        ?
        traits.map((trait, index)=>{
          let {scaleRange} = trait;
          return(
            <ScaleQuestion
              key={index}
              scaleRange={scaleRange}
              selection={data}
              trait={trait}
              isInputHeader={false}
            />
          )
        })
        :
        null
      }
        <ScaleQuestion
          scaleRange={defaultScaleRange}
          selection={data}
          trait={"trait"}
          isInputHeader={true}
        />
        <ScaleQuestion
          scaleRange={defaultScaleRange}
          selection={data}
          trait={"trait"}
          isInputHeader={true}
        />
        <TagQuestion
          selection={data}
          booleanAttributes={booleanAttributes}
        />
      </div>
    );
}

export default Task ;
