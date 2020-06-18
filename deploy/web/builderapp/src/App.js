import React from "react";
import  {HashRouter, Route, Redirect} from "react-router-dom";

import NavBar from "./components/NavBar";
import ExplorePage from "./components/ExplorePage";
import CreatePage from "./components/CreatePage";
import ReviewPage from "./components/ReviewPage";
import WorldBuilderPage from "./components/WorldBuilderPage";
import EditPage from "./components/EditPage";

function App() {
  return (
    <div className="App">
      <HashRouter>
        <Routes />
      </HashRouter>
    </div>
  );
}

export function Routes() {
  return (
    <>
      <NavBar />
      <div style={{ margin: "40px 30px" }}>
        <Route path="/explore" component={ExplorePage} exact/>
        <Route path="/create" component={CreatePage} exact/>
        <Route path="/review" component={ReviewPage} exact/>
        <Route
          path="/world_builder"
          render={props => <WorldBuilderPage {...props} key={Math.random()} exact/>}
        />
        <Route path="/edit/:id" component={EditPage} exact/>
        <Route exact path="/" render={() => <Redirect to="/explore" />} exact/>
      </div>
    </>
  );
}

export default App;
