/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React, {useEffect} from "react";
/* REDUX */
import {useAppDispatch, useAppSelector} from './app/hooks';
//ACTIONS
import {fetchWorlds, setWorldDrafts} from './features/playerWorlds/playerworlds-slice';
/* REACT ROUTER */
import { HashRouter, Route } from "react-router-dom";
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
    const customWorlds = useAppSelector((state) => state.playerWorlds.customWorlds);
    const worldDrafts = useAppSelector((state) => state.playerWorlds.worldDrafts);
    //REDUX ACTIONS
    const fetchPlayerWorlds = ()=>{
      dispatch(fetchWorlds(DummyWorlds))
    }
    // Checks for drafts on local storage then saves them to state.
    const setPlayerWorldDrafts = ()=>{
      let updatedDraft = customWorlds.map((world)=>{
        let worldDraft  = JSON.parse(window.localStorage.getItem(world.id));
        if(worldDraft){
          return worldDraft;
        }else{
          return world;
        }
      })
      console.log("DRAFT  ", updatedDraft)
      dispatch(setWorldDrafts(updatedDraft))
    }
    /* --- LIFE CYCLE FUNCTIONS --- */
    // Pulls worlds from backend
    useEffect(()=>{
      fetchPlayerWorlds()
    },[])
    useEffect(() => {
      setPlayerWorldDrafts()
    }, [customWorlds])
    //WHEN WORLD DRAFTS UPDATE THE WORLD IS SAVED TO LOCAL STORAGE
    useEffect(() => {
      if(worldDrafts){ 
          worldDrafts.map(draft => {
          window.localStorage.setItem(draft.id, JSON.stringify(draft))
        })
      }
    }, [worldDrafts])
    
  return (
      <div>
        <HashRouter>
            <NavHeader/>
            <Route path="/" component={HomePage} exact />
            <Route path="/editworld/:worldId" component={EditWorldPage} exact/>
            <Route path="/editworld/:worldId/:categories" component={EditWorldPage} exact/>
            <Route path="/editworld/:worldId/:categories/map" component={MapPage2} exact/>
            <Route path="/editworld/:worldId/:categories/map/rooms/:roomid" component={RoomPage} exact/>
            <Route path="/editworld/:worldId/:categories/map/rooms/:roomid/characters/:charid" component={CharacterPage} exact/>
            <Route path="/editworld/:worldId/:categories/map/rooms/:roomid/objects/:objectid" component={ObjectPage} exact/>
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