/* REACT */
import React, { useState, useEffect } from 'react';
import { useParams, useRouteMatch, useHistory } from "react-router-dom";
/* REDUX */
import { useAppDispatch, useAppSelector } from '../../../app/hooks';
/* ---- REDUCER ACTIONS ---- */
import { updateSelectedWorld, setWorldDraft } from "../../../features/playerWorld/playerworld-slice.ts";
import { updateRooms, selectRoom } from "../../../features/rooms/rooms-slice.ts";
import { updateObjects, selectObject } from "../../../features/objects/objects-slice.ts";
import { updateCharacters, selectCharacter } from "../../../features/characters/characters-slice.ts";
/* STYLES */
import './styles.css';
/* BOOTSTRAP COMPONENTS */
//LAYOUT
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
/* CUSTOM COMPONENTS */
import GenerateForms from "../../../components/world_builder/FormFields/GenerateForms";
import TextInput from "../../../components/world_builder/FormFields/TextInput";
import InlineTextInsertForm from "../../../components/world_builder/FormFields/InlineTextInsertForm";
import TextButton from "../../../components/world_builder/Buttons/TextButton";
import Button from 'react-bootstrap/Button';
import Slider from "../../../components/world_builder/FormFields/Slider";
import BreadCrumbs from "../../../components/world_builder/BreadCrumbs";
import TypeAheadTokenizerForm from "../../../components/world_builder/FormFields/TypeAheadTokenizer";

const ObjectPage = ({
  api,
  builderRouterNavigate,
}) => {
  let {
    suggestObjectDescription,
    suggestObjectContents
  } = api;

  /* ------ LOCAL STATE ------ */
  const [objectId, setObjectId] = useState("");
  const [parentId, setParentId] = useState("");
  const [objectName, setObjectName] = useState("");
  const [objectPluralName, setObjectPluralName] = useState("");
  const [objectPrefix, setObjectPrefix] = useState("");
  const [objectDesc, setObjectDesc] = useState("");
  const [objectValue, setObjectValue] = useState(0);
  const [objectSize, setObjectSize] = useState(0);
  const [containedObjects, setContainedObjects] = useState([]);

  /* REDUX DISPATCH FUNCTION */
  const dispatch = useAppDispatch();
  /* ------ REDUX STATE ------ */
  //TASKROUTER
  const currentLocation = useAppSelector((state) => state.taskRouter.currentLocation);
  const taskRouterHistory = useAppSelector((state) => state.taskRouter.taskRouterHistory);
  //WORLD
  const worldDraft = useAppSelector((state) => state.playerWorld.worldDraft);
  const selectedWorld = useAppSelector((state) => state.playerWorld.selectedWorld);
  //ROOMS
  const worldRooms = useAppSelector((state) => state.worldRooms.worldRooms);
  const selectedRoom = useAppSelector((state) => state.worldRooms.selectedRoom);
  //OBJECTS
  const worldObjects = useAppSelector((state) => state.worldObjects.worldObjects);
  const selectedObject = useAppSelector((state) => state.worldObjects.selectedObject);
  //CHARACTERS
  const worldCharacters = useAppSelector((state) => state.worldCharacters.worldCharacters);
  /* ------ REDUX ACTIONS ------ */
  //NAVIGATION
  const backStep = ()=>{
    let previousLoc =  taskRouterHistory[taskRouterHistory.length-1]
    console.log("history:  ", taskRouterHistory)
    let updatedHistory = taskRouterHistory.slice(0, taskRouterHistory.length-1);
    console.log("PREVIOUS LOC BACKSTEP:  ", previousLoc)
    builderRouterNavigate(previousLoc)
    dispatch(updateTaskRouterHistory(updatedHistory));
  };
  //WORLD DRAFT
  const updateWorldsDraft = () => {

    dispatch(setWorldDraft(selectedWorld))
  }


  //GENERAL
  //Adds more than one node to currently selected character
  const addContent = (objectId, newNodes)=>{
    let unupdatedWorld = selectedWorld;
    let {objects, nodes } = unupdatedWorld;
    console.log("Object ID:  ", objectId)
    let unupdatedObjectData = nodes[objectId]
    console.log("Object DATA:  ", unupdatedObjectData)
    let updatedNodes = {...nodes};
    let newObjects =[...objects];
    let updatedContainedNodes = {...unupdatedObjectData.contained_nodes};
    newNodes.map((newNode)=>{
        let {classes} = newNode;
        let nodeType = classes[0];
        let formattedNewNode;
        let formattedNewNodetId;
        if(newNode.node_id){
            formattedNewNodetId = newNode.node_id;
            while( objects.indexOf(formattedNewNodetId)>=0){
                let splitformattedNewNodetId = formattedNewNodetId.split("_");
                let idNumber = splitformattedNewNodetId[splitformattedNewNodetId.length-1];
                if((typeof idNumber === "number") && (!Number.isNaN(idNumber))){
                    idNumber = parseInt(idNumber)
                    idNumber = idNumber+1;
                    idNumber = idNumber.toString();
                    splitFormattedObjectId[splitFormattedObjectId.length-1] = idNumber;
                    formattedObjectId = splitFormattedObjectId.join("_");
                }else{
                    formattedObjectId = newNode.name +"_1"
                }
            };
        }else{
            formattedNewNodetId = newNode.name +"_1" ;
        };
        if(nodeType === "object"){
            newObjects.push(formattedNewNodetId);
        };
        formattedNewNode = {...newNode, node_id:formattedNewNodetId , container_node:{target_id: parentId}};
        updatedContainedNodes = {...updatedContainedNodes, [formattedNewNodetId]:{target_id: formattedNewNodetId}};
        updatedNodes = {...updatedNodes, [formattedNewNodetId]:formattedNewNode};
    });
    let updatedObjectData = {...selectedObject, contained_nodes: updatedContainedNodes};
    updatedNodes = {...updatedNodes, [objectId]: updatedObjectData};
    let updatedWorld ={...selectedWorld, objects:[...newObjects], nodes: updatedNodes};
    dispatch(updateSelectedWorld(updatedWorld));
  };


  //OBJECTS
  const addObject = (obj)=>{
    let unupdatedWorld = selectedWorld;
    let {objects, nodes } = unupdatedWorld;
    let formattedObjectId = obj.node_id;
    console.log("OBJECT ADDED:  ", obj)
    //EXISTING OBJECT
    if(obj.node_id){
        console.log("EXISTING OBJECT")
        while(objects.indexOf(formattedObjectId)>=0){
            console.log("FORMATTING OBJECT ID:  ", formattedObjectId)
            let splitFormattedObjectId = formattedObjectId.split("_");
            console.log("SPLIT FORMATTEDOBJECT ID:  ", splitFormattedObjectId)
            let idNumber = parseInt(splitFormattedObjectId[splitFormattedObjectId.length-1]);
            console.log("ID NUMBER:  ", idNumber)
            console.log("ID NUMBER TYPE:  ", typeof (idNumber))
            console.log("ID NUMBER NAN CHECK:  ", !Number.isNaN(idNumber))
            if((typeof idNumber === "number") && (!Number.isNaN(idNumber))){
                console.log("IS A NUMBER  FORMATTED OBJECTID", formattedObjectId)
                console.log("IS A NUMBER  ID NUMBER ", idNumber)
                idNumber = parseInt(idNumber)
                idNumber = idNumber+1;
                idNumber = idNumber.toString();
                splitFormattedObjectId[splitFormattedObjectId.length-1] = idNumber;
                formattedObjectId = splitFormattedObjectId.join("_");
                console.log("IS A NUMBER  FORMATTED RESULT:  ", formattedObjectId)
            }else{
                console.log("NOT A NUMBER  ", formattedObjectId)
                formattedObjectId = obj.name +"_1"
            }
        };
    }else {
        //NEW OBJECT
        console.log("NEW OBJECT")
        formattedObjectId = obj.name +"_1"
    };
    let parentData = selectedObject;
    let updatedObjectData = {...obj, node_id:formattedObjectId, container_node:{target_id: selectedObject.node_id}};
    let updatedObjects = [...objects, formattedObjectId];
    let updatedParentData = {...parentData, contained_nodes:{...parentData.contained_nodes, [formattedObjectId]:{target_id: formattedObjectId}}};
    console.log("UPDATED CHARACTER DATA ON ADD", updatedParentData);
    let updatedNodes = {...nodes, [formattedObjectId]:updatedObjectData, [parentData.node_id]: updatedParentData};
    console.log("UPDATED ADDED OBJECT NODES:  ", updatedNodes);
    let updatedWorld ={...selectedWorld, objects: updatedObjects, nodes:updatedNodes};
    console.log("UPDATED WORLD ADD OBJECT:  ", updatedWorld);
    dispatch(updateSelectedWorld(updatedWorld));
};


  const updateObject = (id, update) => {
    let unupdatedWorld = selectedWorld;
    let { nodes } = unupdatedWorld;
    let updatedNodes = { ...nodes, [id]: update }
    let updatedWorld = { ...selectedWorld, nodes: updatedNodes }
    dispatch(updateSelectedWorld(updatedWorld))
  }
  const deleteObject = (id) => {
    console.log("DELETE OBJECT:  ", id);
    let unupdatedWorld = selectedWorld;
    let {objects } = unupdatedWorld;
    let {contained_nodes} = selectedObject
    let updatedContainedNodes = {...contained_nodes}
    delete updatedContainedNodes[id]
    let updatedObjectData  = {...selectedObject, contained_nodes: updatedContainedNodes }
    let updatedObjects = objects.filter(obj => id !== obj);
    let updatedWorld = containedNodesRemover(id);
    let updatedNodes = {...updatedWorld.nodes, [updatedObjectData.node_id]: updatedObjectData}
    updatedWorld = {...updatedWorld, nodes:updatedNodes}
    console.log("DELETE OBJECT POST NODE REMOVAL WORLD:  ", updatedWorld);
    dispatch(updateSelectedWorld({...updatedWorld, objects: updatedObjects}));
  }

  const deleteSelectedObject = () => {
    let unupdatedWorld = selectedWorld;
    let updatedRoom = selectedWorld.nodes[parentId]
    let updatedRoomContent = { ...updatedRoom.contained_nodes };
    delete updatedRoomContent[objectId];
    unupdatedWorld = { ...unupdatedWorld, nodes: { ...unupdatedWorld.nodes, parentId: updatedRoom } }
    let updatedWorld = containedNodesRemover(objectId)
    let { objects, nodes } = updatedWorld;
    let updatedObjects = objects.filter(obj => objectId !== obj);
    let updatedNodes = { ...nodes };
    delete updatedNodes[objectId];
    updatedWorld = { ...updatedWorld, objects: updatedObjects, nodes: updatedNodes };
    console.log("UPDATED WORLDS UPON OBJECT DELETION:  ", updatedWorld)
    dispatch(setWorldDraft(updatedWorld))
    builderRouterNavigate({ name: "map", id: null })
  }
  //UTILS
  const containedNodesRemover = (nodeId) => {

    console.log("RECURSIVE CONTAINED NODES REMOVER:  ", nodeId)
    const nodeDigger = (id, removalArray) => {
      let { nodes } = selectedWorld;
      let unupdatedNode = nodes[id];
      let { classes, contained_nodes } = unupdatedNode;
      let containedNodes = contained_nodes;
      let containedNodesList = Object.keys(containedNodes);

      if (!containedNodesList.length) {
        removalArray.push({ nodeId: id, class: classes[0] })
        return removalArray
      } else {
        removalArray.push({ nodeId: id, class: classes[0] })
        containedNodesList.map((containedNodeId) => {
          removalArray.push({ nodeId: containedNodeId, class: classes[0] })
          return containedNodesRemover(containedNodeId, removalArray)
        })
      }
    }
    console.log("NODE DIGGER RETURN RESULT", nodeDigger(nodeId, []))
    const removalList = nodeDigger(nodeId, [])

    let { nodes, objects, rooms, agents } = selectedWorld;
    let updatedWorld = selectedWorld;
    removalList.map((removedNode) => {
      let removedNodeClass = removedNode.class;
      let removedNodeId = removedNode.nodeId
      if (removedNodeClass === "agent") {
        let updatedCharacters = agents.filter(char => removedNodeId !== char);
        updatedWorld = { ...updatedWorld, agents: updatedCharacters }
      } else if (removedNodeClass === "object") {
        let updatedObjects = objects.filter(obj => removedNodeId !== obj);
        updatedWorld = { ...updatedWorld, objects: updatedObjects }
      } else if (removedNodeClass === "room") {
        let updatedRooms = rooms.filter(room => removedNodeId !== room);
        updatedWorld = { ...updatedWorld, rooms: updatedRooms }
      }
      console.log("#NODES", nodes)
      let updatedNodes = { ...nodes };
      delete updatedNodes[removedNodeId];
      updatedWorld = { ...updatedWorld, nodes: updatedNodes }
      console.log("NESTED CONTAINED NODE REMOVER", updatedWorld)
    })
    return updatedWorld;
  };

  const worldNodeSorter = (world) => {
    let CharacterNodes = [];
    let RoomNodes = [];
    let ObjectNodes = [];
    const { nodes } = world;
    const WorldNodeKeys = Object.keys(nodes);
    WorldNodeKeys.map((nodeKey) => {
      let WorldNode = nodes[nodeKey];
      if (WorldNode.classes) {
        let NodeClass = WorldNode.classes[0]
        switch (NodeClass) {
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



  //HANDLERS
  const ObjectNameChangeHandler = (e) => {
    let updatedObjectName = e.target.value;
    setObjectName(updatedObjectName)
    let updatedSelectedObject = { ...selectedObject, name: updatedObjectName }
    if (selectedObject) {
      if (selectedObject.node_id) {
        updateObject(selectedObject.node_id, updatedSelectedObject)
      }
    }
  }

  const ObjectDescChangeHandler = (e) => {
    let updatedObjectDesc = e.target.value;
    setObjectDesc(updatedObjectDesc)
    let updatedSelectedObject = { ...selectedObject, desc: updatedObjectDesc }
    if (selectedObject) {
      if (selectedObject.node_id) {
        updateObject(selectedObject.node_id, updatedSelectedObject)
      }
    }
  }

  const ObjectPluralNameChangeHandler = (e) => {
    let updatedObjectPluralName = e.target.value;
    setObjectPluralName(updatedObjectPluralName)
    let updatedSelectedObject = { ...selectedObject, plural: updatedObjectPluralName }
    if (selectedObject) {
      if (selectedObject.node_id) {
        updateObject(selectedObject.node_id, updatedSelectedObject)
      }
    }
  }

  const ObjectPrefixChangeHandler = (e) => {
    let updatedObjectPrefix = e.target.value;
    setObjectPrefix(updatedObjectPrefix)
    let updatedSelectedObject = { ...selectedObject, prefix: updatedObjectPrefix }
    if (selectedObject) {
      if (selectedObject.node_id) {
        updateObject(selectedObject.node_id, updatedSelectedObject)
      }
    }
  }

  const ObjectSizeChangeHandler = (e) => {
    let updatedObjectSize = e.target.value;
    setObjectSize(updatedObjectSize);
    let updatedSelectedObject = { ...selectedObject, size: updatedObjectSize }
    if (selectedObject) {
      if (selectedObject.node_id) {
        updateObject(selectedObject.node_id, updatedSelectedObject)
      }
    }
  }

  const ObjectValueChangeHandler = (e) => {
    let updatedObjectValue = e.target.value;
    setObjectValue(updatedObjectValue)
    let updatedSelectedObject = { ...selectedObject, value: updatedObjectValue }
    if (selectedObject) {
      if (selectedObject.node_id) {
        updateObject(selectedObject.node_id, updatedSelectedObject)
      }
    }
  }

  // COMMON SENSE DESCRIBE OBJECT FUNCTION
  const CommonSenseDescribeObject = () => {
    let target_room = selectedRoom['node_id'];
    let target_id = objectId;
    let nodes = {};
    nodes[target_room] = selectedRoom;
    for (let character of worldCharacters) {
      nodes[character['node_id']] = character;
    }
    for (let object of worldObjects) {
      nodes[object['node_id']] = object;
    }
    let agents = worldCharacters.map(c => c['node_id']);
    let objects = worldObjects.map(c => c['node_id']);
    let rooms = [target_room]
    let room_graph = { nodes, agents, objects, rooms };
    console.log("room graph");
    console.log(room_graph);
    console.log("selectedRoom");
    console.log(target_room);
    suggestObjectDescription({ target_room, room_graph, target_id }).then((result) => {
      console.log("Finished describe object");
      console.log(result);
    })
  }

  // COMMON SENSE CONTENTS OBJECT FUNCTION
  const CommonSenseObjectContents = () => {
    let target_room = selectedRoom['node_id'];
    let target_id = objectId;
    let nodes = {};
    nodes[target_room] = selectedRoom;
    for (let character of worldCharacters) {
      nodes[character['node_id']] = character;
    }
    for (let object of worldObjects) {
      nodes[object['node_id']] = object;
    }
    let agents = worldCharacters.map(c => c['node_id']);
    let objects = worldObjects.map(c => c['node_id']);
    let rooms = [target_room]
    let room_graph = { nodes, agents, objects, rooms };
    console.log("room graph");
    console.log(room_graph);
    console.log("selectedRoom");
    console.log(target_room);
    suggestObjectContents({ target_room, room_graph, target_id }).then((result) => {
      console.log("Finished object contents");
      console.log(result);
      const newItems = result.new_items;
      addContent(target_id, newItems)
    })
  }

  //CRUMBS
  const crumbs = [...taskRouterHistory, currentLocation];

  /* --- LIFE CYCLE FUNCTIONS --- */
  useEffect(() => {
    let updatedObjectData = currentLocation;
    let updatedParentData = taskRouterHistory[taskRouterHistory.length - 1]
    console.log("OBJ ID:  ", updatedObjectData)
    console.log("PARENT ID:  ", updatedParentData)
    if (updatedObjectData) {
      setObjectId(updatedObjectData.id)
    }
    if (updatedParentData) {
      setParentId(updatedParentData.id)
    }
    console.log("WORLD DRAFT:  ", worldDraft)
    dispatch(updateSelectedWorld(worldDraft))
  }, [currentLocation])

  useEffect(() => {
    dispatch(updateSelectedWorld(worldDraft))
  }, [worldDraft])

  useEffect(() => {
    if (selectedWorld) {
      console.log("SELECTED WORLD:  ", selectedWorld)
      worldNodeSorter(selectedWorld)
    }
  }, [selectedWorld])

  useEffect(() => {
    if (parentId) {
      let { nodes } = selectedWorld
      let currentRoom = nodes[parentId]
      console.log("CURRENT PARENT", currentRoom)
      if (currentRoom) {
        dispatch(selectRoom(currentRoom))
      }
    }
  }, [parentId])

  useEffect(() => {
    if (objectId) {
      let { nodes } = selectedWorld
      let currentObject = nodes[objectId]
      console.log("CURRENT OBJECT", currentObject)
      if (currentObject) {
        dispatch(selectObject(currentObject))
      };
    }
  }, [objectId, selectedWorld])

  useEffect(() => {
    if (selectedWorld) {
      const { nodes } = selectedWorld;
      let ObjectNodes = [];
      if (selectedObject) {

        const {
          contain_size,
          contained_nodes,
          desc,
          extra_desc,
          name,
          name_prefix,
          node_id,
          plural,
          size,
          value
        } = selectedObject;

        setObjectName(name)
        setObjectDesc(desc)
        if (!name_prefix) {
          setObjectPrefix("a")
        } else {
          setObjectPrefix(name_prefix)
        }
        if (plural === undefined && (name[name.length - 1] === "s")) {
          let endsWithSDefaultPluralName = `${name}es`
          setObjectPluralName(endsWithSDefaultPluralName)
        } else if (plural === undefined) {
          let defaultPluralName = `${name}s`
          setObjectPluralName(defaultPluralName)
        } else {
          setObjectPluralName(plural)
        }
        setObjectSize(size)
        setObjectValue(value)

        const roomContentNodesKeys = Object.keys(contained_nodes)
        roomContentNodesKeys.map((nodeKey) => {
          let WorldNode = nodes[nodeKey];
          if (WorldNode.classes) {
            let NodeClass = WorldNode.classes[0]
            switch (NodeClass) {
              case "object":
                ObjectNodes.push(WorldNode);
                break;
              default:
                break;
            }
          }
        })
        setContainedObjects(ObjectNodes)
      }
    }
  }, [selectedObject])

  return (
    <Container>
      <BreadCrumbs
        crumbs={crumbs}
      />
      {
        selectedObject
          ?
          <>
            <Row>
              <Col>
                <Row>
                  <TextInput
                    label="Object Name"
                    value={objectName}
                    changeHandler={ObjectNameChangeHandler}
                  />
                </Row>
                <Row>
                  <GenerateForms
                    label="Object Description:"
                    value={objectDesc}
                    changeHandler={ObjectDescChangeHandler}
                    clickFunction={CommonSenseDescribeObject}
                    generateName={"Generate Description"}
                  />
                </Row>
                <Row>
                  <TypeAheadTokenizerForm
                    formLabel="Contents"
                    tokenOptions={worldObjects}
                    sectionName={"objects"}
                    containerId={selectedRoom.node_id}
                    tokens={containedObjects}
                    tokenType={'objects'}
                    onTokenAddition={addObject}
                    onTokenRemoval={deleteObject}
                    builderRouterNavigate={builderRouterNavigate}
                  />
                </Row>
                <Row>
                  <Button onClick={CommonSenseObjectContents} variant="primary">
                    Generate Object Contents
                  </Button>
                </Row>
              </Col>
              <Col>
                <Row>
                  <h5>In-Game appearance:</h5>
                </Row>
                <InlineTextInsertForm
                  formText={objectName}
                  value={objectPrefix}
                  changeHandler={ObjectPrefixChangeHandler}
                  textPlacement="after"

                />
                <Row>
                  <Col xs={2}>
                    <h5>Plural:</h5>
                  </Col>
                  <Col>
                    <InlineTextInsertForm
                      formText="Some"
                      value={objectPluralName}
                      changeHandler={ObjectPluralNameChangeHandler}
                      textPlacement="before"
                    />
                  </Col>
                </Row>
                <Row>
                  <h5>Attributes</h5>
                </Row>
                <Row>
                  <Slider
                    label="Value"
                    maxLabel="Priceless"
                    minLabel="Worthless"
                    value={objectValue}
                    min={0}
                    max={100}
                    changeHandler={ObjectValueChangeHandler}
                  />
                </Row>
                <Row>
                  <Slider
                    label="Size"
                    maxLabel="Big"
                    minLabel="Little"
                    value={objectSize}
                    min={0}
                    max={100}
                    changeHandler={ObjectSizeChangeHandler}
                  />
                </Row>
              </Col>
            </Row>
            <Row>
              <Col>
                <Row>
                  <Col>
                    <TextButton
                      text={selectedObject.node_id ? "Save Changes" : "Create Object"}
                      clickFunction={updateWorldsDraft}
                    />
                  </Col>
                  <Col>
                    <TextButton
                      text={"Delete Object"}
                      clickFunction={deleteSelectedObject}
                    />
                  </Col>
                </Row>
              </Col>
              <Col />
            </Row>
          </>
          : null
      }
    </Container>
  );
}

export default ObjectPage;
