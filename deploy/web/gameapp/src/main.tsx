import * as React from "react";
import { Provider } from "react-redux";
import { ConnectedRouter } from "connected-react-router";
import { Store } from "redux";
import { History } from "history";

import Routes from "./GameRouter";
import { ApplicationState } from "./store";

// Any additional component props go here.
interface MainProps {
  store: Store<ApplicationState>;
  history: History;
}

// Create an intersection type of the component props and our Redux props.
const Main: React.FC<MainProps> = ({ store, history }) => {
  return (
    <Provider store={store}>
      <ConnectedRouter history={history}>{<Routes />}</ConnectedRouter>
    </Provider>
  );
};

export default Main;
