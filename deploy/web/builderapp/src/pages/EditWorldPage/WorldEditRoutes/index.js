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
import Characters from "../EditWorldSections/Characters";
import Objects from "../EditWorldSections/Objects";
import Quests from "../EditWorldSections/Quests";
import Rooms from "../EditWorldSections/Rooms";

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
                        <Rooms/>
                    </Route>
                    <Route path={`${path}/characters`}>
                        <Characters/>
                    </Route>
                    <Route path={`${path}/objects`}>
                        <Objects/>
                    </Route>
                    <Route path={`${path}/interactions`}>
                        <Details/>
                    </Route>
                    <Route path={`${path}/quests`}>
                        <Quests/>
                    </Route>
                </Switch>
            </HashRouter>
        </div>
    );
}

export default Routes;
//<Route exact path="/" render={() => <Redirect to="/explore" />} exact />