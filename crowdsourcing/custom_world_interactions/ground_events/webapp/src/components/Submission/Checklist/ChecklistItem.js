import React, {useState} from "react";

const ChecklistItem = ({
    question,
    data
})=>{
    const checklistFormatFunction =(question, relatedState, checksArr)=>{
        let updatedStatus
        let updatedInstructionsArr =[]
        let formattedCheckListData
        checksArr.map((check)=>{
            switch(check) {
                case "length":
                    updatedStatus = relatedState.length
                    if(!updatedStatus){
                        updatedInstructionsArr.push('Form cannot Be Blank')
                    }
                    break;
                case "not null":
                    updatedStatus = relatedState!==null
                    if(!updatedStatus){
                        updatedInstructionsArr.push('Must make selection')
                    }
                    break;
            }
            formattedCheckListData ={
                question:question,
                status:(!!updatedInstructionsArr.length),
                instructions:updatedInstructionsArr.length? updatedInstructionsArr: ["Done"]
            }
        })
        return formattedCheckListData ;
    }

    return(
        <tr className="checklist-item__row">
            <td className="checklist-item">
                {data.question}
            </td>
            <td className="checklist-item">
                {data.status ? <span style={{color:"green", fontWeight:"bold"}}>COMPLETE</span> : <span style={{color:"red", fontWeight:"bold"}}>INCOMPLETE</span>}
            </td>
        </tr>
    )
}
export default ChecklistItem;
