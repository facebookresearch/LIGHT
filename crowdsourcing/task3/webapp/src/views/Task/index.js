//REACT
import React, { useEffect, useState } from "react";
//STYLING
import "./styles.css"
//CUSTOM COMPONENTS
import Header from "../../components/Header";
import ScaleQuestion from "../../components/Questions/ScaleQuestion";
//COPY
import TaskCopy from "../../TaskCopy";

//Task - Renders component that contains all questionns relevant to task.
const Task = ({
  dummyData,
  dataType,
  setDataType
}) => {
  const {objects, characters, locations} = TaskeCopy;
  const [traits, setTraits]= useState([]);
  const [booleanAttributes, setBooleanAttributes]= useState([]);
  useEffect(()=>{
    if(dataType==="object"){
      const {booleanAttributes, traits}= objects;
      setTraits(traits)
      setBooleanAttributes(booleanAttributes)
    }else if(dataType==="character"){
      const {booleanAttributes, traits}= characters;
      setTraits(traits)
      setBooleanAttributes(booleanAttributes)
    }else if(dataType==="location"){
      const {booleanAttributes, traits}= locations;
      setTraits(traits)
      setBooleanAttributes(booleanAttributes)
    }
  },[dataType])
  const [selectionType, setSelectionType] = useState("object");
  const {trait, scaleRange, actors} = data

    return (
      <div className="task-container">
        <Header/>
        <div>
          {
            dummyData ?
            dummyData.map((selection, index)=>{
              return(
                <div key={index}>
                  <p>
                    {selection.name}
                  </p>
                  <p>
                    {selection.description}
                  </p>
                </div>
              )
            })
            :
            null
          }
        </div>
      {
        traits
        ?
        traits.map((trait, index)=>{
          let {scaleRange} = trait;
          return(
            <ScaleQuestion
              key={index}
              scaleRange={scaleRange}
              selection={dummyData}
              trait={trait}
              isInputHeader={false}
            />
          )
        })
        :
        null
      }
        <ScaleQuestion
          scaleRange={scaleRange}
          selection={dummyData}
          trait={trait}
          isInputHeader={true}
        />
        <ScaleQuestion
          scaleRange={scaleRange}
          selection={dummyData}
          trait={trait}
          isInputHeader={true}
        />
      </div>
    );
}

export default Task ;
