import React, { useState } from "react";

import { FaStar } from "react-icons/fa";
import { Tooltip } from "react-tippy";

const HelpMessage = ({ text }) => {
  const TextArr = text.split("\n");
  const Parchment = TextArr[4];
  const CommandList = TextArr.slice(5, TextArr.length - 2);

  return (
    <div className="helpmessage-container">
      <div className="helpmessage-box">
        <p>
          You pull some scribbled notes on a torn manuscript out of your pocket.
        </p>
        <div className="helpmessage-parchment">
          <p>{Parchment}</p>
          {CommandList.map((para, idx) => (
            <p className="helpmessage-text" key={idx}>
              {para}
            </p>
          ))}
          <p>{Parchment}</p>
        </div>
      </div>
    </div>
  );
};
export default HelpMessage;
