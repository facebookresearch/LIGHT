import React from "react";

import "../../styles.css";

const SettingMessage = (props) => {
  return (
    <div style={{ clear: "both", overflow: "auto" }}>
      <div className="message type-setting">
        {props.text.split("\n").map((para, idx) => (
          <p key={idx}>{para}</p>
        ))}
      </div>
    </div>
  );
};
export default SettingMessage;
