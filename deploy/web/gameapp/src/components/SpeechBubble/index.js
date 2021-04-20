import React from "react";

import "./styles.css";

const SpeechBubble = (props) => {
  const { text } = props;
  return (
    <div className="speechbubble-container">
      <div className="speechbubble bottom">
        <p className="speechbubble-text">{text.toUpperCase()}</p>
      </div>
    </div>
  );
};

export default SpeechBubble;
