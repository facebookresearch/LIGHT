//REACT
import React, {useEffect, useState} from "react";
//STYLING
import "./styles.css"
//CUSTOM COMPONENTS
import InfoIcon from "../../../Icons/Info";
import ToolTip from "../../../ToolTip/index.js"

//ScaleHeader - renders header of ScaleQuestion component displayinng Trait and short description trait
const ScaleHeader = ({
    trait,
    traitDescription,
    isCustom,
    updateFunction,
    toolTip
}) => {

    /*----------------------STATE----------------------*/
    const [traitNameInput, setTraitNameInput] = useState("");
    const [traitDescriptionInput, setTraitDescriptionInput] = useState("");

    /*----------------------EVENTHANDLERS----------------------*/
    const inputChangeHandler = (e)=>{
        let {target} = e;
        let{name, value} =target;
        if(name==="traitName"){
            setTraitNameInput(value);
            updateFunction("name", value)
        }else if(name==="traitDescription"){
            setTraitDescriptionInput(value);
            updateFunction("description", value)
        }
    }
    return (
        <div className="scaleheader-container">
            {isCustom
             ?
            <>
                <input
                    className="scaleheader-input"
                    type="text" name={"traitName"}
                    value={traitNameInput}
                    onChange={inputChangeHandler}
                    placeholder="Enter custom trait name here"
                />
                <input
                    className="scaleheader-input"
                    type="text" name={"traitDescription"}
                    value={traitDescriptionInput}
                    onChange={inputChangeHandler}
                    placeholder="Enter a description for this trait"
                />
            </>
            :
            <>
                <p className="scaleheader-trait__text">{`${trait}  -  `}</p>
                <p className="scaleheader-description__text">{traitDescription}</p>
            </>
            }
            <ToolTip
                toolTipText={toolTip}
            >
                <div>
                    <InfoIcon/>
                </div>
            </ToolTip>
        </div>
    );
};

export default ScaleHeader;