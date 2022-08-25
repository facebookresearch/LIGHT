/* REACT */
import React from "react";
/* REDUX */
import { useAppSelector } from "./app/hooks";
//ROUTES
import Routes from "./GameRouter";
//STYLES
import "./styles.css";

function App() {
  /* ----REDUX STATE---- */
  //TUTORIAL;
  const inHelpMode = useAppSelector((state) => state.tutorials.inHelpMode);

  return (
    <div id={`${inHelpMode ? "helpmode" : ""}`}>
      <Routes />
    </div>
  );
}

export default App;
