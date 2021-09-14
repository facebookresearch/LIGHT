/* REACT */
import React from "react";
/* STYLES */
import "./styles.css";

// DisconnectMessage - Renders Disconnect messagee and reload link upon player being idle for too long
const DisconnectMessage = () => {
  return (
    <div className="disconnect-container">
      <h2 className="disconnect-text">
        You have been disconnected due to inactivity.
      </h2>
      <h2
        onClick={() => window.location.reload()}
        style={{ textDecoration: "underline" }}
        className="disconnect-text__reload"
      >
        Click Here to re-enter world.
      </h2>
    </div>
  );
};

export default DisconnectMessage;
