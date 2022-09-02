import React, {useState} from "react";

import ChecklistItem from "./ChecklistItem"

import "./styles.css";

const Checklist = ({
    data, header, headerColor
})=>{

    return(
        <div className="checklist-container">
            <div className="checklist-header__container">
                <p className="checklist-header__text" style={{color:headerColor}}>
                    {header}
                </p>
            </div>
            <table className="checklist-table">
                <thead>
                    <tr className="checklist-table__header--row">
                        <th className="checklist-table__header--text">
                            Status
                        </th>
                        <th className="checklist-table__header--text">
                            Question
                        </th>
                    </tr>
                </thead>
                <tbody>
                    {data.map((data, index)=> <ChecklistItem key={index} data={data} />)}
                </tbody>
            </table>
        </div>
    )
}
export default Checklist;
