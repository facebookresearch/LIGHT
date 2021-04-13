import React from "react";

import "./styles.css";

const SpeechBubble = (props) => {
  const { text } = props;
  return <div className="speechbubble bottom">{text}</div>;
};

export default SpeechBubble;
