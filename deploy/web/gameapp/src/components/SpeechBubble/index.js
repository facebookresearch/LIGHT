import React from "react";

import "./styles.css";

const SpeechBubble = (props) => {
  const { text } = props;
  return (
    <div className="speechbubble-container">
      <div className="speechbubble left">
        <div className="speechbubble-tail" />
        <p className="speechbubble-text">{text ? text.toUpperCase() : null}</p>
      </div>
    </div>
  );
};

export default SpeechBubble;
