/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React, {useEffect, useState} from "react";
/* REDUX */
import { useAppDispatch, useAppSelector } from "../../app/hooks";

/* STYLES */
import "./styles.css";
/* CUSTOM COMPONENTS */
import TaskToolBar from "../../components/TaskToolBar";
import PreviewContent from "../../Views/PreviewView/PreviewContent";
import MapPage2 from "../builder_pages/MapPage2";
/* BOOTSTRAP COMPONENTS */
import Form from 'react-bootstrap/Form';
import Modal from 'react-bootstrap/Modal';
import Button from 'react-bootstrap/Button';

const BuilderRouter = ({virtualPath, api}) => {
  // TODO will likely need to do something similar to the router for the full builder
  // Perhaps we can use a MemoryRouter from the react router package?
  return <MapPage2 api={api} />;
}

const App = ({
  api,
  handleSubmit
})=>{
  /* ------ REDUX STATE ------ */
  // VIEW STATE
  // TODO configure loading the world state? Below is dummy
  const [currentWorld, updateWorld] = useState({});
  /*---------------LOCAL STATE----------------*/

  // TODO I'm not sure what the right call is for replacing the router
  // to work with the 4 intended views
  const [virtualPath, setVirtualPath] = useState("");
  const [workerComments, setWorkerComments] = useState("");
  const [showInstructions, setShowInstructions] = useState(false);
  const [show, setShow] = useState(false);
  /* ----REDUX ACTIONS---- */
  // REDUX DISPATCH FUNCTION
  const dispatch = useAppDispatch();

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
    let workerSubmission = {
      data: currentWorld,
      comments: workerComments
    }
    handleSubmit(workerSubmission)
    setShow(false)
  }

  const isWorldBigEnough = () => {
    return true; // TODO actually check room, char, obj counts
  }

  /*---------------LIFECYCLE----------------*/

  return (
  <>
    <div className="task-container">
      <TaskToolBar
        buttonFunction={OpenModal}
        toggleFunction={ToggleInstructionsModal}
        toggleValue={showInstructions}
      />
      <div className="builder-container">
        <BuilderRouter virtualPath={virtualPath} api={api} />
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
