//REACT
import React from "react";
import ReactDOM from "react-dom";
//REDUX
import { Provider } from "react-redux";
import { store } from "./app/store";
//STYLES
import "./index.css";
//CUSTOM  COMPONENTS
import App from "./App";
//TOOLS
import reportWebVitals from "./reportWebVitals";

ReactDOM.render(
  <React.StrictMode>
    <Provider store={store}>
      <App />
    </Provider>
  </React.StrictMode>,
  document.getElementById("root")
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
