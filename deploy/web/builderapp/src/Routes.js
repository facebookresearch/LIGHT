/* REACT */
import React, {useEffect} from "react";
/* REDUX */
import {useAppDispatch, useAppSelector} from './app/hooks';
//ACTIONS
import {fetchWorlds} from './features/playerWorlds/playerworlds-slice';
/* REACT ROUTER */
import { HashRouter, Route, Redirect } from "react-router-dom";
/* CUSTOM COMPONENTS */
import NavHeader from "./components/NavHeader"
//PAGES
import HomePage from "./pages/HomePage";
import EditWorldPage from "./pages/EditWorldPage";
import MapPage2 from "./pages/MapPage2"
import RoomPage from "./pages/RoomPage"
import CharacterPage from "./pages/CharacterPage"
import ObjectPage from "./pages/ObjectPage"

//ORIGINALPAGES
import ExplorePage from "./components/ExplorePage";
import CreatePage from "./components/CreatePage";
import ReviewPage from "./components/ReviewPage";
import WorldBuilderPage from "./components/WorldBuilderPage";
import EditPage from "./components/EditPage";
//Dummy Data
import DummyWorlds from "./Copy/DummyData"

const Routes = ()=> {
    //DUMMY DATA
  /* ----REDUX ACTIONS---- */
    // REDUX DISPATCH FUNCTION
    const dispatch = useAppDispatch();
    //REDUX STATE
    const fetchPlayerWorlds = ()=>{
      dispatch(fetchWorlds(DummyWorlds))
    }
    /* --- LIFE CYCLE FUNCTIONS --- */
    useEffect(()=>{
      fetchPlayerWorlds()
    },[])
  return (
      <div>
        <HashRouter>
            <NavHeader/>
            <Route path="/" component={HomePage} exact />
            <Route path="/editworld/:worldId" component={EditWorldPage} exact/>
            <Route path="/editworld/:worldId/:categories" component={EditWorldPage} exact/>
            <Route path="/editworld/:worldId/:categories/map" component={MapPage2} exact/>
            <Route path="/editworld/:worldId/:categories/map/rooms/:roomid" component={RoomPage} exact/>
            <Route path="/editworld/:worldId/:categories/map/rooms/:roomid/character/:charid" component={CharacterPage} exact/>
            <Route path="/editworld/:worldId/:categories/map/rooms/:roomid/object/:objectid" component={ObjectPage} exact/>
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