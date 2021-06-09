import React from "react";

const DataCard = ({header, body, color}) => {
    return (
       <div className="card-container">
           <div className="card-header__container" style={{backgroundColor: color}}>
                {header()}
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
