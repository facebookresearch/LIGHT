import React from "react";
import { BrowserRouter as Router, Route, Redirect } from "react-router-dom";

import NavBar from "./components/NavBar";
import ExplorePage from "./components/ExplorePage";
import CreatePage from "./components/CreatePage";
import ReviewPage from "./components/ReviewPage";
import WorldBuilderPage from "./components/WorldBuilderPage";
import EditPage from "./components/EditPage";

function App() {
  return (
    <div className="App">
      <Router>
        <Routes />
      </Router>
    </div>
  );
}

export function Routes() {
  return (
    <>
      <NavBar />
      <div style={{ margin: "40px 30px" }}>
        <Route path="/explore" component={ExplorePage} />
        <Route path="/create" component={CreatePage} />
        <Route path="/review" component={ReviewPage} />
        <Route
          path="/world_builder"
          render={props => <WorldBuilderPage {...props} key={Math.random()} />}
        />
        <Route path="/edit/:id" component={EditPage} />
        <Route exact path="/" render={() => <Redirect to="/explore" />} />
      </div>
    </>
  );
}

export default App;
