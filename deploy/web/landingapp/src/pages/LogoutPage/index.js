import React from "react";

import "../../styles.css";

import Unicorn from "../../assets/images/unicorn.jpg";

const LogoutPage = (props) => {
  return (
    <div className="logoutpage-container">
      <div
        className="main-container"
        style={{
          backgroundColor: "#697b4d",
          alignItems: "center",
          height: "90%",
          padding: "3em",
        }}
      >
        <h1 style={{ color: "white" }}>Terms</h1>
      </div>
    </div>
  );
};

export default LogoutPage;
