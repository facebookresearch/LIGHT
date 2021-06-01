import React, {useEffect, useState} from "react";
import "./styles.css";

//CUSTOM COMPONENTS
import ObjectButton from "./ObjectButton";

const MultipleChoiceQuestion = ({question, answers})=>{
    const [selectedItem, setSelectedItem] = useState(null);
    const [objectList, setObjectList] = useState([])

    const clickHandler = (id, selection)=>{
        setSelectedItem(id);
        selectFunction(selection);
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
                objectList.map((item, index)=><ObjectButton key={index} name={item} selectFunction={()=>clickHandler(index, item)} isSelected={selectedItem==index} />)
                :
                null
            }
            </div>
        </div>
    )
}
export default MultipleChoiceQuestion;
