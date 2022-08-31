
/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

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