import React from "react";
import Logo from "../../Logo";

function LoadingScreen({ isFull }) {
  console.log(isFull);
  const [isTimedOut, setTimedOut] = React.useState(false);
  const TIMEOUT_SECONDS = 10;

  React.useEffect(() => {
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
    <div
      style={{
        height: "100%",
        width: "100%",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        flexDirection: "column",
      }}
    >
      <div style={{ width: 500 }}>
        <div style={{ width: 300 }}>
          <Logo />
        </div>
        <div style={{ fontSize: 20, marginTop: 50, fontStyle: "italic" }}>
          {msg}
        </div>
      </div>
    </div>
  );
}

export default LoadingScreen;
