/* REACT */
import React from "react";
/* STYLES */
import "./styles.css";

const SettingMessage = (props) => {
  return (
    <div style={{ display: "flex", justifyContent: "center", width: "100%" }}>
      <div className="message type-setting">
        {props.text.split("\n").map((para, idx) => (
          <p key={idx}>{para}</p>
        ))}
      </div>
    </div>
  );
};
export default SettingMessage;
