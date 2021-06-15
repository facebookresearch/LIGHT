import React, {useState} from "react";

const ChecklistItem = ({
    data
})=>{

    return(
        <tr className="checklist-item__row">
            <td className="checklist-item">
                {data.status ? <span style={{color:"green", fontWeight:"bold"}}>COMPLETE</span> : <span style={{color:"red", fontWeight:"bold"}}>INCOMPLETE</span>}
            </td>
            <td className="checklist-item">
                {data.question}
            </td>
        </tr>
    )
}
export default ChecklistItem;
