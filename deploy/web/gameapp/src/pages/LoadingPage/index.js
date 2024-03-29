/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React, {useEffect} from "react";
/* CUSTOM COMPONENTS */
import Logo from "../../Logo";

//LoadingScreen - renders loading screen when loading, and error screen when connection times out or when server is full
const LoadingScreen = ({ isFull }) => {
  const [isTimedOut, setTimedOut] = React.useState(false);
  const TIMEOUT_SECONDS = 10;

  useEffect(() => {
    if (!isTimedOut) {
      const timer = setTimeout(() => {
        setTimedOut(true);
      }, TIMEOUT_SECONDS * 1000);
      return () => clearTimeout(timer);
    }
  }, [isTimedOut, setTimedOut]);

  let msg = <span></span>;
  if (isFull) {
    const builder_url =
      window.location.protocol + "//" + window.location.host + "/builder/";
    msg = (
      <p>
        Sorry, the base world is filled with players right now, you'll need to
        return later... Or, create your own world and share it with friends
        using the World Builder.
        <br />
        <a href={builder_url} rel="noopener noreferrer" target="_blank">
          Go To World Builder.
        </a>
      </p>
    );
  } else if (isTimedOut) {
    msg = (
      <span>
        It's been {TIMEOUT_SECONDS} seconds, there's likely a server issue.
      </span>
    );
  } else {
    msg = <span>Hang tight. You are entering a new world...</span>;
  }

  return (
    <div className="_loading-page_ h-screen w-screen flex justify-center items-center">
      <div className="_loading-body_ w-1/2 h-1/2 flex flex-col justify-center items-center text-white">
        <div className="_loading-logo-container_ w-full">
          <Logo />
        </div>
        <div className="_loading-message-container_ flex flex-row justify-center items-center">
          <div className="_loading-spinner_ hidden sm:hidden md:flex radial-progress animate-spin mr-4" style={{"--value":75}}/>
          <span className="_loading-message-text_ text-lg md:text-xl text-center">{msg}</span>
        </div>
      </div>
    </div>
  );
};

export default LoadingScreen;