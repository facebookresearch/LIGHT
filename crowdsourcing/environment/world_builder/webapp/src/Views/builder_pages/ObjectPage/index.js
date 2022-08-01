/* REACT */
import React, { useState, useEffect } from 'react';
/* REDUX */
import { useAppDispatch, useAppSelector } from '../../../app/hooks';
/* ---- REDUCER ACTIONS ---- */
//NAVIGATION
import {updateTaskRouterHistory, setTaskRouterCurrentLocation} from '../../../features/taskRouter/taskrouter-slice';
//LOADING
import { setIsLoading} from "../../../features/loading/loading-slice.ts";
//ERROR
import { setShowError, setErrorMessage} from "../../../features/errors/errors-slice.ts";
//WORLD
import { updateSelectedWorld, setWorldDraft } from "../../../features/playerWorld/playerworld-slice.ts";
//ROOMS
import { updateRooms, selectRoom } from "../../../features/rooms/rooms-slice.ts";
//OBJECTS
import { updateObjects, selectObject } from "../../../features/objects/objects-slice.ts";
//CHARACTERS
import { updateCharacters, selectCharacter} from "../../../features/characters/characters-slice.ts";
/* STYLES */
import './styles.css';
/* BOOTSTRAP COMPONENTS */
//LAYOUT
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
/* CUSTOM COMPONENTS */
//FORMS
import TypeAheadTokenizerForm from "../../../components/world_builder/FormFields/TypeAheadTokenizer";
import GenerateForms from "../../../components/world_builder/FormFields/GenerateForms";
import TextInput from "../../../components/world_builder/FormFields/TextInput";
import InlineTextInsertForm from "../../../components/world_builder/FormFields/InlineTextInsertForm";
//BUTTONS
import TextButton from "../../../components/world_builder/Buttons/TextButton";
import GenerateButton from "../../../components/world_builder/Buttons/GenerateButton";
//INPUT COMPONENTS
import Slider from "../../../components/world_builder/FormFields/Slider";
//BREADCRUMBS
import BreadCrumbs from "../../../components/world_builder/BreadCrumbs";

//ObjectPage - Advanced edit page for Selected Object allows user to modify all of object's attributes
const ObjectPage = ({
  api,
  builderRouterNavigate,
}) => {

  //API
  let {
    suggestObjectDescription,
    suggestObjectContents
  } = api;

  /* ------ LOCAL STATE ------ */
  const [selectedParent, setSelectedParent] = useState(null);
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
  //LOADING
  const isLoading = useAppSelector((state) => state.loading.isLoading);
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
  const selectedCharacter = useAppSelector((state)=> state.worldCharacters.selectedCharacter);
  /* ------ REDUX ACTIONS ------ */
  //LOADING
  const startLoading = () =>{
    dispatch(setIsLoading(true));
  };
  const stopLoading = () =>{
      dispatch(setIsLoading(false));
  };

  //ERROR
  const showError = ()=>{
      dispatch(setShowError(true));
  };
  const setError = (errorMessage)=>{
      dispatch(setErrorMessage(errorMessage));
  };
  //NAVIGATION
  const backStep = ()=>{
    let previousLoc =  taskRouterHistory[taskRouterHistory.length-1]
    let updatedHistory = taskRouterHistory.slice(0, taskRouterHistory.length-1);
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
    console.log("NEW NODES:  ", newNodes);
    let unupdatedWorld = selectedWorld;
    let {objects, nodes } = unupdatedWorld;
    let unupdatedObjectData = nodes[objectId];
    console.log("UNUPDATED OBJECT DATA:  ", unupdatedObjectData);
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
        formattedNewNode = {...newNode, node_id:formattedNewNodetId , container_node:{target_id: objectId}};
        updatedContainedNodes = {...updatedContainedNodes, [formattedNewNodetId]:{target_id: formattedNewNodetId}};
        updatedNodes = {...updatedNodes, [formattedNewNodetId]:formattedNewNode};
    });
    let updatedObjectData = {...selectedObject, contained_nodes: updatedContainedNodes};
    console.log("UPDATED OBJECT DATA:  ", updatedObjectData);
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
        while(objects.indexOf(formattedObjectId)>=0){
            let splitFormattedObjectId = formattedObjectId.split("_");
            let idNumber = parseInt(splitFormattedObjectId[splitFormattedObjectId.length-1]);
            if((typeof idNumber === "number") && (!Number.isNaN(idNumber))){
                idNumber = parseInt(idNumber)
                idNumber = idNumber+1;
                idNumber = idNumber.toString();
                splitFormattedObjectId[splitFormattedObjectId.length-1] = idNumber;
                formattedObjectId = splitFormattedObjectId.join("_");
            }else{
                formattedObjectId = obj.name +"_1" ;
            };
        };
    }else {
        //NEW OBJECT
        formattedObjectId = obj.name +"_1" ;
    };
    let parentData = selectedObject;
    let updatedObjectData = {...obj, node_id:formattedObjectId, container_node:{target_id: selectedObject.node_id}};
    let updatedObjects = [...objects, formattedObjectId];
    let updatedParentData = {...parentData, contained_nodes:{...parentData.contained_nodes, [formattedObjectId]:{target_id: formattedObjectId}}};
    let updatedNodes = {...nodes, [formattedObjectId]:updatedObjectData, [parentData.node_id]: updatedParentData};
    let updatedWorld ={...selectedWorld, objects: updatedObjects, nodes:updatedNodes};
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
    let unupdatedWorld = selectedWorld;
    let {objects } = unupdatedWorld;
    let {contained_nodes} = selectedObject;
    let updatedContainedNodes = {...contained_nodes};
    delete updatedContainedNodes[id];
    let updatedObjectData  = {...selectedObject, contained_nodes: updatedContainedNodes };
    let updatedObjects = objects.filter(obj => id !== obj);
    let updatedWorld = containedNodesRemover(id);
    let updatedNodes = {...updatedWorld.nodes, [updatedObjectData.node_id]: updatedObjectData}
    updatedWorld = {...updatedWorld, nodes:updatedNodes};
    dispatch(updateSelectedWorld({...updatedWorld, objects: updatedObjects}));
  };

  const deleteSelectedObject = () => {
    let unupdatedWorld = selectedWorld;
    let updatedParent = selectedWorld.nodes[parentId]
    let updatedParentContent = { ...updatedRoom.contained_nodes };
    delete updatedParentContent[objectId];
    updatedParent = {...updatedParent, contained_nodes: updatedParentContent}
    unupdatedWorld = { ...unupdatedWorld, nodes: { ...unupdatedWorld.nodes, parentId: updatedParent } }
    let updatedWorld = containedNodesRemover(objectId)
    let { objects, nodes } = updatedWorld;
    let updatedObjects = objects.filter(obj => objectId !== obj);
    let updatedNodes = { ...nodes };
    delete updatedNodes[objectId];
    updatedWorld = { ...updatedWorld, objects: updatedObjects, nodes: updatedNodes };
    dispatch(setWorldDraft(updatedWorld));
    backStep();
  };
  //UTILS
  const containedNodesRemover = (nodeId) => {
    const nodeDigger = (id, removalArray) => {
      let { nodes } = selectedWorld;
      let unupdatedNode = nodes[id];
      let { classes, contained_nodes } = unupdatedNode;
      let containedNodes = contained_nodes;
      let containedNodesList = Object.keys(containedNodes);

      if (!containedNodesList.length) {
        removalArray.push({ nodeId: id, class: classes[0] });
        return removalArray;
      } else {
        removalArray.push({ nodeId: id, class: classes[0] });
        containedNodesList.map((containedNodeId) => {
          removalArray.push({ nodeId: containedNodeId, class: classes[0] });
          return containedNodesRemover(containedNodeId, removalArray);
        });
      };
    };
    const removalList = nodeDigger(nodeId, []);

    let { nodes, objects, rooms, agents } = selectedWorld;
    let updatedWorld = selectedWorld;
    removalList.map((removedNode) => {
      let removedNodeClass = removedNode.class;
      let removedNodeId = removedNode.nodeId;
      if (removedNodeClass === "agent") {
        let updatedCharacters = agents.filter(char => removedNodeId !== char);
        updatedWorld = { ...updatedWorld, agents: updatedCharacters };
      } else if (removedNodeClass === "object") {
        let updatedObjects = objects.filter(obj => removedNodeId !== obj);
        updatedWorld = { ...updatedWorld, objects: updatedObjects };
      } else if (removedNodeClass === "room") {
        let updatedRooms = rooms.filter(room => removedNodeId !== room);
        updatedWorld = { ...updatedWorld, rooms: updatedRooms };
      };
      let updatedNodes = { ...nodes };
      delete updatedNodes[removedNodeId];
      updatedWorld = { ...updatedWorld, nodes: updatedNodes };
    });
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
      let {classes} = WorldNode;
      let nodeClass = classes[0]
      if (nodeClass) {
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
        };
      };
    });
    dispatch(updateRooms(RoomNodes));
    dispatch(updateObjects(ObjectNodes));
    dispatch(updateCharacters(CharacterNodes));
  };



  //HANDLERS
  //OBJECT CHANGE HANDLERS
  //Handles changes to selected object's name
  const ObjectNameChangeHandler = (e) => {
    let updatedObjectName = e.target.value;
    setObjectName(updatedObjectName);
    let updatedSelectedObject = { ...selectedObject, name: updatedObjectName };
    if (selectedObject) {
      if (selectedObject.node_id) {
        updateObject(selectedObject.node_id, updatedSelectedObject);
      };
    };
  };

  //Handles changes to selected object's description
  const ObjectDescChangeHandler = (e) => {
    let updatedObjectDesc = e.target.value;
    setObjectDesc(updatedObjectDesc);
    let updatedSelectedObject = { ...selectedObject, desc: updatedObjectDesc }
    if (selectedObject) {
      if (selectedObject.node_id) {
        updateObject(selectedObject.node_id, updatedSelectedObject);
      };
    };
  };

  //Handles changes to selected object's pluralized name
  const ObjectPluralNameChangeHandler = (e) => {
    let updatedObjectPluralName = e.target.value;
    setObjectPluralName(updatedObjectPluralName);
    let updatedSelectedObject = { ...selectedObject, plural: updatedObjectPluralName };
    if (selectedObject) {
      if (selectedObject.node_id) {
        updateObject(selectedObject.node_id, updatedSelectedObject);
      };
    };
  };

  //Handles changes to selected object's prefix
  const ObjectPrefixChangeHandler = (e) => {
    let updatedObjectPrefix = e.target.value;
    setObjectPrefix(updatedObjectPrefix);
    let updatedSelectedObject = { ...selectedObject, prefix: updatedObjectPrefix };
    if (selectedObject) {
      if (selectedObject.node_id) {
        updateObject(selectedObject.node_id, updatedSelectedObject);
      };
    };
  };

  //Handles changes to selected object's size
  const ObjectSizeChangeHandler = (e) => {
    let updatedObjectSize = e.target.value;
    setObjectSize(updatedObjectSize);
    let updatedSelectedObject = { ...selectedObject, size: updatedObjectSize };
    if (selectedObject) {
      if (selectedObject.node_id) {
        updateObject(selectedObject.node_id, updatedSelectedObject);
      };
    };
  };

  //Handles changes to selected object's value
  const ObjectValueChangeHandler = (e) => {
    let updatedObjectValue = e.target.value;
    setObjectValue(updatedObjectValue);
    let updatedSelectedObject = { ...selectedObject, value: updatedObjectValue };
    if (selectedObject) {
      if (selectedObject.node_id) {
        updateObject(selectedObject.node_id, updatedSelectedObject);
      };
    };
  };
  //GENERATE HANDLERS
  //Generates contained objects for object
  const generateContainedObjectsButtonFunction = async ()=>{
    try{
        const payload = await CommonSenseObjectContents();
        const {nodeId, data} = payload;
        console.log("PAY LOAD", payload)
        addContent(nodeId, data);
        dispatch(setIsLoading(false));
    } catch (error) {
      stopLoading();
      console.log(error);
      errorHandler(error);
    };
  };

  const generateObjectDescButtonFunction = async ()=>{
    try{
        const payload = await CommonSenseDescribeObject();
        const {nodeId, data} = payload;
        console.log("Object Description", payload)
        updateObject(nodeId, data);
        stopLoading();
    } catch (error) {
        stopLoading();
        console.log(error);
        errorHandler(error);
    };
  };

  /* ------ END OF HANDLERS ------ */

  /* COMMON SENSE API INTERACTIONS */
  // COMMON SENSE OBJECT DESCRIPTION GENERATION FUNCTION
  const CommonSenseDescribeObject = async () => {
    try{
      startLoading()
      let target_room = selectedRoom['node_id'];
      console.log(" TARGET ROOM:  ", target_room)
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
      const result = await suggestObjectDescription({ target_room, room_graph, target_id })
      console.log("Finished describe object");
      console.log(result);
      const generatedData = result.updated_item;
      const updatedDesc = generatedData.desc;
      const updatedObject = {...selectedObject, desc: updatedDesc};
      console.log(updatedObject);
      const payload = {
          nodeId: target_id,
          data: updatedObject
      };
      return payload;
    } catch (error){
      stopLoading();
      errorHandler(error);
      throw error;
    };
  };

  // COMMON SENSE OBJECT CONTENTS GENERATION FUNCTION
  const CommonSenseObjectContents = async () => {
    try{
      startLoading()
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
      const result = await suggestObjectContents({ target_room, room_graph, target_id })
      console.log("Finished Describe");
      console.log(result);
      const newItems = result.new_items;
      const payload = {
          nodeId: target_id,
          data: newItems
      };
      return payload;
    } catch (error){
      stopLoading();
      errorHandler(error);
      throw error;
    }
  }

  //CRUMBS
  const crumbs = [...taskRouterHistory, currentLocation];
  console.log("CRUMBS", crumbs)
  /* --- LIFE CYCLE FUNCTIONS --- */
  useEffect(() => {
    let updatedObjectData = currentLocation;
    let updatedParentData = taskRouterHistory[taskRouterHistory.length - 1];
    console.log("OBJECT DATA:  ", updatedObjectData);
    console.log("PARENT DATA:  ", updatedParentData);
    if (updatedObjectData) {
      setObjectId(updatedObjectData.id);
    };
    if (updatedParentData) {
      setParentId(updatedParentData.id);
    };
    dispatch(updateSelectedWorld(worldDraft));
  }, [currentLocation]);

  useEffect(() => {
    dispatch(updateSelectedWorld(worldDraft));
  }, [worldDraft]);

  useEffect(() => {
    if (selectedWorld) {
      worldNodeSorter(selectedWorld);
    };
  }, [selectedWorld]);

  useEffect(() => {
    if (parentId) {
      let { nodes } = selectedWorld;
      let currentParent = nodes[parentId];
      setSelectedParent(currentParent)
    };
  }, [parentId]);

  useEffect(() => {
    if (objectId) {
      let { nodes } = selectedWorld;
      let currentObject = nodes[objectId];
      if (currentObject) {
        dispatch(selectObject(currentObject));
      };
    };
  }, [objectId, selectedWorld]);

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

        setObjectName(name);
        setObjectDesc(desc);
        if (!name_prefix) {
          setObjectPrefix("a");
        } else {
          setObjectPrefix(name_prefix);
        };
        if (plural === undefined && (name[name.length - 1] === "s")) {
          let endsWithSDefaultPluralName = `${name}es` ;
          setObjectPluralName(endsWithSDefaultPluralName);
        } else if (plural === undefined) {
          let defaultPluralName = `${name}s` ;
          setObjectPluralName(defaultPluralName);
        } else {
          setObjectPluralName(plural);
        };
        setObjectSize(size);
        setObjectValue(value);

        const roomContentNodesKeys = Object.keys(contained_nodes)
        roomContentNodesKeys.map((nodeKey) => {
          let WorldNode = nodes[nodeKey];
          let {classes} = WorldNode
          if (classes) {
            let NodeClass = classes[0]
            switch (NodeClass) {
              case "object":
                ObjectNodes.push(WorldNode);
                break;
              default:
                break;
            };
          };
        });
        setContainedObjects(ObjectNodes);
      };
    };
  }, [selectedObject]);

  return (
    <Container>
      <BreadCrumbs
        crumbs={crumbs}
      />
      {
        (selectedObject || selectedParent)
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
                    clickFunction={generateObjectDescButtonFunction}
                    generateButtonLabel={"Generate Description"}
                    isLoading={isLoading}
                  />
                </Row>
                <Row>
                  <TypeAheadTokenizerForm
                    formLabel="Contents"
                    tokenOptions={worldObjects}
                    sectionName={"objects"}
                    containerId={selectedObject.node_id}
                    tokens={containedObjects}
                    tokenType={'objects'}
                    onTokenAddition={addObject}
                    onTokenRemoval={deleteObject}
                    builderRouterNavigate={builderRouterNavigate}
                  />
                </Row>
                <Row>
                  <GenerateButton
                    label={"Generate Object Contents"}
                    clickFunction={generateContainedObjectsButtonFunction}
                    isLoading={isLoading}
                  />
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
