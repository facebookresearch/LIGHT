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
import MapPage2 from "../builder_pages/MapPage2";
import BuilderRouter from "./BuilderRouter"
/* BOOTSTRAP COMPONENTS */
import Form from 'react-bootstrap/Form';
import Modal from 'react-bootstrap/Modal';
import Button from 'react-bootstrap/Button';
/* DEFAULT WORLD */
import DefaultWorld from "../../StartingWorldCopy";

// const BuilderRouter = ({virtualPath, api}) => {
//   // TODO will likely need to do something similar to the router for the full builder
//   // Perhaps we can use a MemoryRouter from the react router package?
//   return <MapPage2 api={api} />;
// }

const App = ({
  api,
  handleSubmit
})=>{
  //REDUX STATE
  const selectedWorld = useAppSelector((state) => state.playerWorld.selectedWorld);
  const worldDraft = useAppSelector((state) => state.playerWorld.worldDraft);
  /* ------ REDUX STATE ------ */
  //TASKROUTER
  const currentLocation = useAppSelector((state) => state.taskRouter.currentLocation);
  const taskRouterHistory = useAppSelector((state) => state.taskRouter.taskRouterHistory);
  // VIEW STATE
  const [currentWorld, updateWorld] = useState({});
  /*---------------LOCAL STATE----------------*/

  // TODO I'm not sure what the right call is for replacing the router
  // to work with the 4 intended views
  const [workerComments, setWorkerComments] = useState("");
  const [showInstructions, setShowInstructions] = useState(false);
  const [show, setShow] = useState(false);
  // REDUX DISPATCH FUNCTION
  const dispatch = useAppDispatch();
  /* ----REDUX ACTIONS---- */
  //Updates current selectedWorld state
  const setSelectedWorld = (newWorldData)=>{
    dispatch(updateSelectedWorld(newWorldData))
  }

  /*---------------HANDLERS----------------*/
  const OpenModal = ()=>{
    setShow(true)
  }

  const ToggleInstructionsModal = ()=>{
    let updatedToggleValue = !showInstructions
    setShowInstructions(updatedToggleValue)
  }

  const CommentChangeHandler = (e)=>{
    let updatedWorkerComments = e.target.value;
    setWorkerComments(updatedWorkerComments)
  }

  const SubmissionHandler = ()=>{
    let updatedCurrentWorld = JSON.parse(window.localStorage.getItem("taskWorld"))
    let workerSubmission = {
      data: updatedCurrentWorld,
      comments: workerComments
    }
    handleSubmit(workerSubmission)
    setShow(false)
  }

  const isWorldBigEnough = () => {
    return true; // TODO actually check room, char, obj counts
  }

  /*---------------LIFECYCLE----------------*/
  //Initial pull to set default world as draft
  useEffect(() => {
    let initialDraft  = JSON.parse(window.localStorage.getItem("taskWorld"))
    console.log("INITIAL DRAFT:  ", initialDraft)
    console.log("INITIAL DRAFT BOOLEAN:  ", (!initialDraft))
    if(!initialDraft){
      window.localStorage.setItem("taskWorld", JSON.stringify(DefaultWorld))
      dispatch(setWorldDraft(DefaultWorld))
    }else {
      dispatch(setWorldDraft(initialDraft))
    }
    window.localStorage.setItem("currentLocation", JSON.stringify("/"))

  }, [])

  return (
  <>
    <div className="task-container">
      <TaskToolBar
        buttonFunction={OpenModal}
        toggleFunction={ToggleInstructionsModal}
        toggleValue={showInstructions}
      />
      <div className="builder-container">
        <BuilderRouter api={api} />
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
}

export default App;
