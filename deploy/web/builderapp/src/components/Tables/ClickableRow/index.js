/* REACT */
import React from "react";
/* REDUX */

/* STYLES */
import "./styles.css";
/* BOOTSTRAP COMPONENTS */

/* CUSTOM COMPONENTS */
import TableCell from "../TableCell";

const ClickableRow = ({
    rowFields,
    rowData
 }) => {
     return(
                <tr>
                   {rowFields.map((field)=><TableCell field={field.key} data={rowData}/>)}
                </tr>
     )
 }

 export default ClickableRow