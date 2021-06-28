//REACT
import React, {useState} from "react";
//KONVA
//STYLING
import "./styles.css"
//CUSTOM COMPONENTS

const ScaleRange = ({trait, actors}) => {

  return (
    <div style={{width:"100%", display:"flex", justifyContent:"space-between", backgroundColor:"grey"}}>
        <p>
            MIN
        </p>
        <p>
            {trait.name}
        </p>
        <p>
            MAX
        </p>
    </div>
  );
};

export default ScaleRange;
