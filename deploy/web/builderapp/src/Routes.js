/* REACT */
import React from "react";
/* REACT ROUTER */
import { HashRouter, Route, Redirect } from "react-router-dom";
/* CUSTOM COMPONENTS */
import NavHeader from "./components/NavHeader"
//PAGES
import HomePage from "./pages/HomePage";
import EditWorldPage from "./pages/EditWorldPage";
//ORIGINALPAGES
import ExplorePage from "./components/ExplorePage";
import CreatePage from "./components/CreatePage";
import ReviewPage from "./components/ReviewPage";
import WorldBuilderPage from "./components/WorldBuilderPage";
import EditPage from "./components/EditPage";

const Routes = ()=> {
  return (
      <div>
        <HashRouter>
            <NavHeader/>
            <Route path="/" component={HomePage} exact />
            <Route path="/editworld/:worldId" component={EditWorldPage} />
            <Route path="/explore" component={ExplorePage} exact />
            <Route path="/create" component={CreatePage} exact />
            <Route path="/review" component={ReviewPage} exact />
            <Route
            path="/world_builder"
            render={(props) => (
                <WorldBuilderPage {...props} key={Math.random()} exact />
            )}
            />
            <Route path="/edit/:id" component={EditPage} exact />
        </HashRouter>
      </div>
  );
}

export default Routes;
//<Route exact path="/" render={() => <Redirect to="/explore" />} exact />