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
import Table from 'react-bootstrap/Table'
/* CUSTOM COMPONENTS */
import SearchBar from "./SearchBar"
import ClickableRow from "./ClickableRow";

const GeneralTable = ({
    hasSearchBar,
    data,
    fields
 }) => {
     return(
         <div>
             {hasSearchBar ? <SearchBar/> :null}
             <Table bordered hover>
                <thead>
                    <tr>
                        {fields.map((field)=><th>{field.label}</th>)}
                    </tr>
                </thead>
                <tbody>
                    {
                        data.length ?
                        data.map(entry => <ClickableRow rowFields={fields} rowData={entry}/>)
                        :
                        null
                    }
                </tbody>
             </Table>
         </div>
     )
 }

 export default GeneralTable