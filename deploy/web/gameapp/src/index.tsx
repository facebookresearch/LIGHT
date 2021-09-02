//REACT
import React from "react";
import ReactDOM from "react-dom";
//REDUX
import { Provider } from "react-redux";
import store from "./store";
//ROUTER
import GameRouter from "./GameRouter";

const rootElement = document.getElementById("root");

ReactDOM.render(
  <Provider store={store}>
    <GameRouter />
  </Provider>,
  rootElement
);
