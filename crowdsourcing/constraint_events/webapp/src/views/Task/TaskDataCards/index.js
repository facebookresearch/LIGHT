import React from "react";
//Style
import "./styles.css";
//Custom Components
import DataCard from "./DataCard";

const TaskDataCards = ({object1, object2, interaction}) => {
    const obj1Name = object1.name.toUpperCase()
    const obj2Name = object2.name.toUpperCase()
    return (
       <div className="taskdatacards-container">
            <div className="items-container">
                <DataCard
                    header={()=><p className="card-header__text" >{obj1Name}</p>}
                    body={object1.desc}
                    color="blue"
                />
                <DataCard
                    header={()=><p className="card-header__text" >{obj2Name}</p>}
                    body={object2.desc}
                    color="orange"
                />
            </div>
            <div className="desc-container">
                <DataCard
                    header={()=><p className="card-header__text">Interaction Description: Use <span style={{color:"blue"}}>{obj1Name}</span> with <span style={{color:"orange"}}>{obj2Name}</span></p>}
                    body={interaction}
                    color="green"
                />
            </div>
       </div>
    );
}

export default TaskDataCards ;
