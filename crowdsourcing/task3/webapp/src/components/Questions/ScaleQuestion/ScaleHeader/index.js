//REACT
import React, {useEffect, useState} from "react";
//STYLING
import "./styles.css"

//ScaleHeader - renders header of ScaleQuestion component displayinng Trait and short description trait
const ScaleHeader = ({trait, traitDescription}) => {

    return (
        <div className="scaleheader-container">
            <p className="scaleheader-trait__text">{trait}</p>
            <p className="scaleheader-description__text">{traitDescription}</p>
        </div>
    );
};

export default ScaleHeader;
