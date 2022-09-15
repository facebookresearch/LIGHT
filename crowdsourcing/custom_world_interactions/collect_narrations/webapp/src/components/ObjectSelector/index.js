import React, {useEffect, useState} from "react";
import "./styles.css";

//CUSTOM COMPONENTS
import ObjectButton from "./ObjectButton";

const ObjectSelector = ({label, selectedItem, items, selectFunction})=>{
    const [selectedDesc, setSelectedDesc] = useState("");
    const [objectList, setObjectList] = useState([])

    const clickHandler = (selection)=>{
        setSelectedDesc(selection.desc);
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
                    isSelected={selectedItem ? selectedItem==item.name : false}
                />
                ))
                :
                null
            }
            </div>
            {selectedItem ? <p className="selection-description" ><span style={{fontWeight:"bold"}}>{selectedItem.toUpperCase()}:  </span>{selectedDesc}</p> : null}
        </div>
    )
}
export default ObjectSelector;
