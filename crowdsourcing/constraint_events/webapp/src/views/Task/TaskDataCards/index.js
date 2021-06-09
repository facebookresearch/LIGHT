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
                    header={obj1Name}
                    body={object1.desc}
                    color="blue"
                />
                <DataCard
                    header={obj2Name}
                    body={object2.desc}
                    color="orange"
                />
            </div>
            <div className="desc-container">
                <DataCard
                    header={"Interaction Description: Use # with #"}
                    keywords={[{color:"blue", item:obj1Name}, {color:"orange", item:obj2Name}]}
                    body={interaction}
                    color="green"
                />
            </div>
       </div>
    );
}

export default TaskDataCards ;
