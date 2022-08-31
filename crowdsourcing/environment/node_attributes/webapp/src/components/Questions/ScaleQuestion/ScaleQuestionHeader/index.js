/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

//REACT
import React, {useEffect, useState} from "react";
//STYLING
import "./styles.css"

//ScaleHeader - renders header of ScaleQuestion component displayinng Trait and short description trait
const ScaleHeader = ({
    trait,
    traitDescription,
    isCustom,
    updateFunction
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
        </div>
    );
};

export default ScaleHeader;
