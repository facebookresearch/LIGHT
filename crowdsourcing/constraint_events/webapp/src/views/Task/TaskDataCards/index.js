import React from "react";

import "./styles.css";

import DataCard from "./DataCard";

const TaskDataCards = ({object1, object2, interaction}) => {
    return (
       <div className="taskdatacards-container">
            <div className="items-container">
                <DataCard
                    header={object1.name}
                    body={object1.desc}
                    color="blue"
                />
                <DataCard
                    header={object2.name}
                    body={object2.desc}
                    color="orange"
                />
            </div>
            <div className="desc-container">
                <DataCard
                    header="Interaction Description"
                    body={interaction}
                    color="green"
                />
            </div>
       </div>
    );
}

export default TaskDataCards ;
