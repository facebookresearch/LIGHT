//REACT
import React from "react";

const Header = ({headerText})=>{
    return(
        <div className="header">
            <h1 className="header__text">{headerText}</h1>
        </div>
    )
}

export default Header;
