import React, { useState, useEffect } from "react";
import "./styles.css";

const Logo = (props) => {
  const builder_url =
    window.location.protocol + "//" + window.location.host + "/builder/";
  return (
    <div className="header">
      <img alt="logo" src="/scribe.png" />
      <div className="logo-container">
        <h1 className="logo-title">LIGHT</h1>
        <p className="logo-text">
          Learning in Interactive Games with Humans and Text
        </p>
        {/*<Link to="/profile">
          <h3>
          My Profile
          </h3>
          </Link>
        <p>
          <a href={builder_url} rel="noopener noreferrer" target="_blank">
            Go To World Builder
          </a>
        </p>*/}
      </div>
    </div>
  );
};

export default Logo;
