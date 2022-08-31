/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

//REACT
import React from "react";
//Custom Components
import FormatQuestion from "../../../components/Utils/FormatQuestion";

//DataCard - renders formatted card with object and interaction data
const DataCard = ({
    header, //Header text
    body, //  Body text
    color, // header background and container border color
    keywords // Keywords that will replace # in Format question function
}) => {
    return (
       <div className="card-container">
           <div className="card-header__container" style={{backgroundColor: color}}>
                <FormatQuestion
                    question={header}
                    keywords={keywords}
                    containerStyle="card-header__text"
                />
           </div>
           <div className="card-body__container" style={{borderColor:color}}>
               <p className="card-body__text">
                {body}
               </p>
           </div>
       </div>
    );
}

export default DataCard ;
