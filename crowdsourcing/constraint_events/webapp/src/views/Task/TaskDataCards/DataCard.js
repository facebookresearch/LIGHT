import React from "react";

import "./styles.css"

const DataCard = ({header, body, color}) => {
    return (
       <div className="card-container">
           <div className="card-header__container" style={{backgroundColor: color}}>
               <p className="card-header__text">
                {header}
               </p>
           </div>
           <div className="card-body__container">
               <p className="card-body__text">
                {body}
               </p>
           </div>
       </div>
    );
}

export default DataCard ;
