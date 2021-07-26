//REACT
import React, {useEffect, useState} from "react";
//STYLING
import "./styles.css"
import { Typeahead } from 'react-bootstrap-typeahead'; // ES2015

//ScaleHeader - renders header of ScaleQuestion component displayinng Trait and short description trait
const ScaleHeader = ({
    trait,
    traitDescription,
    isInputHeader
}) => {
    const [traitNameInput, setTraitNameInput] = useState("");
    const [traitDescriptionInput, setTraitDescriptionInput] = useState("");
    const inputChangeHandler = (e)=>{
        let {target} = e;
        let{name, value} =target;
        if(name==="traitName"){
            setTraitNameInput(value);
        }else if(name==="traitDescription"){
            setTraitDescriptionInput(value);
        }

    }
    return (
        <div className="scaleheader-container">
            {isInputHeader ?
            <>
                <label className="scaleheader-trait__text">
                    TRAIT NAME
                </label>
                <Typeahead
                    id="basic-typeahead-single"
                    className="scaleheader-input"
                    type="text" name={"traitName"}
                    value={traitNameInput}
                    onChange={inputChangeHandler}
                    options={["strength", "dexterity", "stamina"]}
                />
                <label className="scaleheader-description__text">
                    TRAIT DESCRIPTION
                </label>
                <input className="scaleheader-input" type="text" name={"traitDescription"} value={traitDescriptionInput} onChange={inputChangeHandler}/>
            </>
            :
            <>
                <p className="scaleheader-trait__text">{trait}</p>
                <p className="scaleheader-description__text">{traitDescription}</p>
            </>
            }
        </div>
    );
};

export default ScaleHeader;
