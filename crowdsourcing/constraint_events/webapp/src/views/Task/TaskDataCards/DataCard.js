import React from "react";
import FormatQuestion from "../../../components/Utils/FormatQuestion";

const DataCard = ({header, body, color, keywords}) => {
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
