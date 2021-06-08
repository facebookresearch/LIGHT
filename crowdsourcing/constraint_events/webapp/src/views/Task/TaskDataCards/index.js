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
                />
                <DataCard
                    header={object2.name}
                    body={object2.desc}
                />
            </div>
            <div className="desc-container">
            <DataCard
                header="Action Description"
                body={interaction}
            />
            </div>
       </div>
    );
}

export default TaskDataCards ;
