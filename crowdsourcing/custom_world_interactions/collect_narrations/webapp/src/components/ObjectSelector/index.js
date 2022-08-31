
/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React, {useEffect, useState} from "react";
import "./styles.css";

//CUSTOM COMPONENTS
import ObjectButton from "./ObjectButton";

const ObjectSelector = ({label, items, selectFunction})=>{
    const [selectedItem, setSelectedItem] = useState(null);
    const [objectList, setObjectList] = useState([])

    const clickHandler = (selection)=>{
        setSelectedItem(selection);
        selectFunction(selection.name);
    }
    useEffect(()=>{
        setObjectList(items)
    }, [items])
    return(
        <div className="selector-container" >
            <h1 className="selector-header">
                {label}
            </h1>
            <div className="options-container">
            {
                [objectList].length
                ?
                objectList.map((item, index)=>(
                <ObjectButton
                    key={index}
                    name={item.name}
                    selectFunction={()=>clickHandler(item)}
                    isSelected={selectedItem ? selectedItem.name==item.name : false}
                />
                ))
                :
                null
            }
            </div>
            {selectedItem ? <p className="selection-description" ><span style={{fontWeight:"bold"}}>{selectedItem.name.toUpperCase()}:  </span>{selectedItem.desc}</p> : null}
        </div>
    )
}
export default ObjectSelector;
