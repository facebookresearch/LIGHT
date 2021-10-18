/* REACT */
import React from "react";
/* REDUX */

/* STYLES */
import "./styles.css";
/* BOOTSTRAP COMPONENTS */

/* CUSTOM COMPONENTS */


const TableCell = ({
    field,
    data
 }) => {
     return(
        <td>{data[field]}</td> 
     )
 }

 export default TableCell