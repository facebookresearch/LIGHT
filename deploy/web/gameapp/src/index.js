import React from "react";
import ReactDOM from "react-dom";

import GameRouter from "./GameRouter";
import Game from "./pages/GamePage";

const rootElement = document.getElementById("root");

ReactDOM.render(<GameRouter />, rootElement);
