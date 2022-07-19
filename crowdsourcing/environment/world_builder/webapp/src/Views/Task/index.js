/* REACT */
import React, {useEffect, useState} from "react";
/* REDUX */
import { useAppDispatch, useAppSelector } from "../../app/hooks";
//ACTIONS
import {setWorldDraft, updateSelectedWorld} from '../../features/playerWorld/playerworld-slice.ts';
/* STYLES */
import "./styles.css";
/* CUSTOM COMPONENTS */
import TaskToolBar from "../../components/TaskToolBar";
import PreviewContent from "../../Views/PreviewView/PreviewContent";
import BuilderRouter from "./BuilderRouter"
/* BOOTSTRAP COMPONENTS */
import Form from 'react-bootstrap/Form';
import Modal from 'react-bootstrap/Modal';
import Button from 'react-bootstrap/Button';
import Spinner from 'react-bootstrap/Spinner'
import Alert from 'react-bootstrap/Alert';
/* DEFAULT WORLD */
import DefaultWorld from "../../StartingWorldCopy";

const App = ({
  api,
  handleSubmit
})=>{
  /* ------ LOCAL STATE ------  */
  const [workerComments, setWorkerComments] = useState("");
  const [showInstructions, setShowInstructions] = useState(false);
  const [show, setShow] = useState(false);
  /* ------ REDUX STATE ------ */
  //WORLDS
  const worldDraft = useAppSelector((state) => state.playerWorld.worldDraft);
  //ROOMS
  const worldRooms = useAppSelector((state) => state.worldRooms.worldRooms);
  //CHARACTERS
  const worldCharacters = useAppSelector((state) => state.worldCharacters.worldCharacters);
  //OBJECTS
  const worldObjects = useAppSelector((state) => state.worldObjects.worldObjects);
  // REDUX DISPATCH FUNCTION
  const dispatch = useAppDispatch();
  /* ----REDUX ACTIONS---- */
  //Updates current selectedWorld state
  const setSelectedWorld = (newWorldData)=>{
    dispatch(updateSelectedWorld(newWorldData));
  };

  /*---------------HANDLERS----------------*/
  const OpenModal = ()=>{
    setShow(true);
  };

  const ToggleInstructionsModal = ()=>{
    let updatedToggleValue = !showInstructions;
    setShowInstructions(updatedToggleValue);
  };

  //Updates text in comments section of submission form
  const CommentChangeHandler = (e)=>{
    let updatedWorkerComments = e.target.value;
    setWorkerComments(updatedWorkerComments);
  };

  //Submission Handler - Will submit the worker's comments and world from local storage then clear the local storage upon successful submission of their complted draft
  const SubmissionHandler = ()=>{
    let updatedCurrentWorld = JSON.parse(window.localStorage.getItem("taskWorld"))
    let workerSubmission = {
      data: updatedCurrentWorld,
      comments: workerComments
    };
    handleSubmit(workerSubmission);
    setShow(false);
  };

  //A function that will run each time the world builder saves a draft and will alert worker wor when they have completed the task
  const isWorldBigEnough = () => {
    return true; // TODO actually check room, char, obj counts
  };

  /*---------------LIFECYCLE----------------*/
  //This lifecycle evnt will attempt to pull a draft from local storage data first, if there is none it will pull
  //the default world from the StartingWorldCopy.js file
  useEffect(() => {
    let initialDraft  = JSON.parse(window.localStorage.getItem("taskWorld"));
    if(!initialDraft){
      window.localStorage.setItem("taskWorld", JSON.stringify(DefaultWorld));
      dispatch(setWorldDraft(DefaultWorld));
    }else {
      dispatch(setWorldDraft(initialDraft));
    }
    window.localStorage.setItem("currentLocation", JSON.stringify("/"));
  }, []);

  //Each time the worldDraft Redux state is updated the localStorage draft will be updated as well.
  useEffect(() => {
      //*** NOTE *** be sure to collect worker ID and use it as local storage key
      window.localStorage.setItem("taskWorld", JSON.stringify(worldDraft));
      setSelectedWorld(worldDraft);
  }, [worldDraft]);

  return (
  <>
    <div className="task-container">
      <TaskToolBar
        buttonFunction={OpenModal}
        toggleFunction={ToggleInstructionsModal}
        toggleValue={showInstructions}
        roomCount={worldRooms.length}
        charCount={worldCharacters.length}
        objectCount={worldObjects.length}
      />
      <div className="builder-container">
        <BuilderRouter api={api} />
        <Spinner animation="border" variant="primary" />
      </div>
      <Modal
        show={show}
        onHide={() => setShow(false)}
        dialogClassName="modal-90w"
      >
        <Modal.Header >
          <Modal.Title id="modal-header">
            Submit Session Data
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {
            (isWorldBigEnough())
            ?
            <>
              <p>
                Are you sure you are finished with this session?
              </p>
              <div>
              <Form>
                <Form.Group className="mb-3" >
                  <Form.Label>TASK COMMENTS AND FEEDBACK</Form.Label>
                  <Form.Control value={workerComments} onChange={CommentChangeHandler} as="textarea" rows={4} />
                </Form.Group>
              </Form>
              </div>
              <div>
                <Button variant="success" onClick={SubmissionHandler}>Submit</Button>{' '}
                <Button variant="danger" onClick={() => setShow(false)}>Cancel</Button>{' '}
              </div>
            </>
            :
            <>
              <p>
                {`To complete this task you must create a larger world. TODO add details for what that means`}
              </p>
              <div>
                <Button variant="danger" onClick={() => setShow(false)}>Return to task</Button>{' '}
              </div>
            </>
          }
        </Modal.Body>
      </Modal>
      <Modal
        show={showInstructions}
        onHide={() => setShowInstructions(false)}
        dialogClassName="modal-90w"
      >
        <Modal.Header closeButton>
          <Modal.Title id="modal-header">
            INSTRUCTIONS
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <PreviewContent/>
        </Modal.Body>
      </Modal>
    </div>
  </>
  );
};
export default App;
