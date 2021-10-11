/* REACT */
import React from "react";
/* REACT ROUTER */
import { 
    HashRouter, 
    Route,
    Switch,
    Redirect,  
    useParams,
    useRouteMatch
 } from "react-router-dom";
/* CUSTOM COMPONENTS */
//SECTIONS
import Details from "../EditWorldSections/Details";

const Routes = ()=> {
    let { path, url } = useRouteMatch();
    return (
        <div>
            <HashRouter>
                <Switch>
                    <Route path={`${path}/details`}>
                        <Details/>
                    </Route>
                    <Route path={`${path}/rooms`}>
                        <Details/>
                    </Route>
                    <Route path={`${path}/characters`}>
                        <Details/>
                    </Route>
                    <Route path={`${path}/objects`}>
                        <Details/>
                    </Route>
                    <Route path={`${path}/interactions`}>
                        <Details/>
                    </Route>
                    <Route path={`${path}/quests`}>
                        <Details/>
                    </Route>
                </Switch>
            </HashRouter>
        </div>
    );
}

export default Routes;
//<Route exact path="/" render={() => <Redirect to="/explore" />} exact />