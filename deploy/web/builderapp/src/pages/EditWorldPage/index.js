/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React, { useEffect } from 'react';
import { useParams, useRouteMatch, useHistory } from "react-router-dom";
/* REDUX */
import {useAppDispatch, useAppSelector} from '../../app/hooks';
/* ---- REDUCER ACTIONS ---- */
import { fetchWorlds, selectWorld } from "../../features/playerWorlds/playerworlds-slice.ts";
import { updateRooms} from "../../features/rooms/rooms-slice.ts";
import { updateObjects} from "../../features/objects/objects-slice.ts";
import { updateCharacters } from "../../features/characters/characters-slice.ts";
import { setLeftSidebar } from "../../features/sidebars/sidebars-slice.ts";
/* STYLES */
import './styles.css';
/* BOOTSTRAP COMPONENTS */
//LAYOUT
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
/* CUSTOM COMPONENTS */
import SideBarDrawer from "../../components/SideBarDrawer"
import WorldEditBody from "./WorldEditBody"
import ButtonGroups from "../../components/ButtonGroups"
//Dummy Data
import DummyWorlds from "../../Copy/DummyData"

const EditWorldPage = ()=> {
  //REACT ROUTER
  const history = useHistory();
  let { worldId, categories } = useParams();
  //let { path, url } = useRouteMatch();
  /* REDUX DISPATCH FUNCTION */
  const dispatch = useAppDispatch();
  /* ------ REDUX STATE ------ */
  //WORLDS
  const customWorlds = useAppSelector((state) => state.playerWorlds.customWorlds);
  const selectedWorld = useAppSelector((state) => state.playerWorlds.selectedWorld);
  //DRAWER
  const showLeftDrawer = useAppSelector((state) => state.sidebars.showLeftSidebar);
  /* REDUX ACTIONS */

  const closeRightSidebar = () => dispatch(setLeftSidebar(false));

  const handleClick = (sectionName)=>{
    history.push(`/editworld/${worldId}/${sectionName}`);
  }

  const WorldNodeSorter = (world)=>{
    let CharacterNodes = [];
    let RoomNodes = [];
    let ObjectNodes = [];
    const {nodes} = world;
    const WorldNodeKeys = Object.keys(nodes);
    WorldNodeKeys.map((nodeKey)=>{
      let WorldNode = nodes[nodeKey];
      if(WorldNode.classes){
        let NodeClass = WorldNode.classes[0]
        switch(NodeClass) {
          case "agent":
            CharacterNodes.push(WorldNode);
            break;
          case "object":
            ObjectNodes.push(WorldNode);
            break;
          case "room":
            RoomNodes.push(WorldNode);
            break;
          default:
            break;
          }
        }
      })
      dispatch(updateRooms(RoomNodes))
      dispatch(updateObjects(ObjectNodes))
      dispatch(updateCharacters(CharacterNodes))
  }
    /* --- LIFE CYCLE FUNCTIONS --- */
    useEffect(()=>{
      dispatch(fetchWorlds(DummyWorlds))
    },[])

    useEffect(()=>{
      if(customWorlds.length){
        customWorlds.map((world) =>{
          const {id} = world;
          if(worldId == id){
            dispatch(selectWorld(world))
          }
        })
      }
    },[customWorlds])

    useEffect(()=>{
      if(selectedWorld){
        WorldNodeSorter(selectedWorld)
      }
    },[selectedWorld])

  const SideBarButtons = [
    {
      name: "details",
      clickFunction: () => handleClick("details"),
      activeCondition: (categories == "details" || !categories)
    },
    {
      name: "characters",
      clickFunction: () => handleClick("characters"),
      activeCondition: (categories == "characters")
    },
    {
      name: "rooms",
      clickFunction: () => handleClick("rooms"),
      activeCondition: (categories == "rooms")
    },
    {
      name: "quests",
      clickFunction: () => handleClick("quests"),
      activeCondition: (categories == "quests")
    },
    {
      name: "objects",
      clickFunction: () => handleClick("objects"),
      activeCondition: (categories == "objects")
    },
    {
      name: "interactions",
      clickFunction: () => handleClick("interactions"),
      activeCondition: (categories == "interactions")
    }
  ];
  
  return (
    <Container>
      <Row>
        <Col xs={3}>
          <ButtonGroups
            buttons={SideBarButtons}
          />
        </Col>
        <Col>
          <WorldEditBody/>
        </Col>
      </Row>
    </Container>
  );
}

export default EditWorldPage;