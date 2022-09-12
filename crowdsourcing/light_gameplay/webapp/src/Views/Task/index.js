
/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React, {useEffect, useState} from "react";
/* REDUX */
import { useAppDispatch, useAppSelector } from "../../app/hooks";
import {addMessage, clearMessages} from "../../features/workerActivity/workerActivity-slice";
/* STYLES */
import "./styles.css";
/* CUSTOM COMPONENTS */
import TaskToolBar from "../../components/TaskToolBar";
import PreviewContent from "../../Views/PreviewView/PreviewContent";
/* BOOTSTRAP COMPONENTS */
import Form from 'react-bootstrap/Form';
import Modal from 'react-bootstrap/Modal';
import Button from 'react-bootstrap/Button';

//DO MINIMUM
const MINIMUM_NUMBER_OF_DOS = 10;
//SAY MINIMUM
const MINIMUM_NUMBER_OF_SAYS = 15;

const App = ({
  url,
  handleSubmit
})=>{
  /* ------ REDUX STATE ------ */
  // VIEW STATE
  const LightMessageList = useAppSelector((state) => state.workerActivity.LightMessageList);
  /*---------------LOCAL STATE----------------*/

  const [workerData, setWorkerData] = useState([]);
  const [workerComments, setWorkerComments] = useState("");
  const [activityCounter, setActivityCounter] = useState(0);
  const [sayCounter, setSayCounter] = useState(0);
  const [doCounter, setDoCounter] = useState(0);
  const [showInstructions, setShowInstructions] = useState(false);
  const [show, setShow] = useState(false);
  /* ----REDUX ACTIONS---- */
  // REDUX DISPATCH FUNCTION
  const dispatch = useAppDispatch();
  const AddLightMessage = (msg) => {
      dispatch(addMessage(msg));
  };
  const ClearPlayerMessages = () => {
    dispatch(clearMessages());
};

  /*---------------HANDLERS----------------*/
  const DataUpdateHandler = (data)=>{
    AddLightMessage(data)
  }

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
    let reports = workerData.filter((entry) => {return entry.caller == 'report'});
    let nonReports = workerData.filter((entry) => {return entry.caller != 'report'});
    let workerSubmission = {
      data: nonReports.map((entry) => {return {text: entry.text, caller: entry.caller, actor: entry?.actor?.name}}),
      reports: reports,
      comments: workerComments
    }
    handleSubmit(workerSubmission)
    setShow(false)
  }

  /*---------------LIFECYCLE----------------*/
  useEffect(() => {
    ClearPlayerMessages()
    const handler = event => {
      let data;
      try {
        data = JSON.parse(event.data)
      } catch {
        // Pass - Json data didn't exist, maybe another event?
        return
      }
      DataUpdateHandler(data)
    }

    window.addEventListener("message", handler)
    return () => window.removeEventListener("message", handler)
  }, [])

  useEffect(() => {
    setWorkerData(LightMessageList)
  }, [LightMessageList])

  useEffect(() => {
    let nonReports = workerData.filter((entry) => {return entry.caller !== 'report'});
    let errorEvents = nonReports.filter(msg => msg.caller == 'ErrorEvent');
    let workerActivity = nonReports.filter(msg => msg.is_self);
    let workerActivityCount = workerActivity.length;
    setActivityCounter(workerActivityCount)
    let workerSaidActivity = workerActivity.filter(msg=>{
      let {text}=msg;
      let isTell = text.indexOf('tell');
      let openingQuote = text.indexOf('"');
      let closingQuote = text[text.length-1]
      return ((openingQuote>=0) || (isTell>=0 && closingQuote === '"') )
    })
    let updatedWorkerSayCount = workerSaidActivity.length;
    let updatedWorkerDoCount = workerActivityCount - updatedWorkerSayCount - errorEvents.length;
    setSayCounter(updatedWorkerSayCount);
    setDoCounter(updatedWorkerDoCount);
  }, [workerData])

  return (
  <>
    {
      url
      ?
    <div className="task-container">
        <TaskToolBar
          doCounter={doCounter}
          sayCounter={sayCounter}
          buttonFunction={OpenModal}
          toggleFunction={ToggleInstructionsModal}
          toggleValue={showInstructions}
        />
        <div className="iframe-container">
            <iframe
                src={url}
                width="100%"
                height="100%"
            >

            </iframe>
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
            ((MINIMUM_NUMBER_OF_SAYS <= sayCounter) && (MINIMUM_NUMBER_OF_DOS <= doCounter))
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
                {`To complete this task you must submit a minimum of ${MINIMUM_NUMBER_OF_DOS} do actions and ${MINIMUM_NUMBER_OF_SAYS} said actions`}
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
    :null
    }
  </>
  );
}

export default App;
