import React from "react";

import "./styles.css";

const SpeechBubble = (props) => {
  const { text } = props;
  return (
    <div className="speechbubble bottom">
      <p style={{ textAlign: "center", padding: "0", margin: "0" }}>
        {text.toUpperCase()}
      </p>
    </div>
  );
};

export default SpeechBubble;
