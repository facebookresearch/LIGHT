import React from "react";

import "./styles.css"

import Copy from "../../TaskCopy"

const {taskHeader} = Copy;

const Header = () => {
    return (
        <div className="header">
            <h1 className="header__text">{taskHeader}</h1>
        </div>
    );
}

export default Header ;
