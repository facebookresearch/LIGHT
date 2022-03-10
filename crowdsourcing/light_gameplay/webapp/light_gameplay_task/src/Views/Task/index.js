/* REACT */
import React, {useEffect, useState} from "react";
/* REDUX */
import { useAppDispatch, useAppSelector } from "../../app/hooks"
import {addMessage} from "../../features/workerActivity/workerActivity-slice"
/* STYLES */
import "./styles.css"
/* CUSTOM COMPONENTS */
import TaskToolBar from "../../components/TaskToolBar"
/* BOOTSTRAP COMPONENTS */
import Modal from 'react-bootstrap/Modal'
import Button from 'react-bootstrap/Button'


const App = ()=>{
  /* ------ REDUX STATE ------ */
  // VIEW STATE
  const LightMessageList = useAppSelector((state) => state.workerActivity.LightMessageList);
  const activityCounter = useAppSelector((state) => state.workerActivity.counter);
  /*---------------LOCAL STATE----------------*/
  const [workerData, setWorkerData] = useState([]);
  const [show, setShow] = useState(false);
  /* ----REDUX ACTIONS---- */
  // REDUX DISPATCH FUNCTION
  const dispatch = useAppDispatch();
  const AddLightMessage = (msg) => {
      dispatch(addMessage(msg));
  };

  /*---------------HANDLERS----------------*/
  const DataUpdateHandler = (data)=>{

    AddLightMessage(data)
  }

  const OpenModal = ()=>{
    setShow(true)
  }

  const SubmissionHandler = ()=>{
    console.log("SESSION DATA:  ", workerData)
    setShow(false)
  }

  /*---------------LIFECYCLE----------------*/
  useEffect(() => {
    const handler = event => {
      console.log("EVENT", event)
      const data = JSON.parse(event.data)
      DataUpdateHandler(data)
    }

    window.addEventListener("message", handler)
    return () => window.removeEventListener("message", handler)
  }, [])

  useEffect(() => {
    setWorkerData(LightMessageList)
  }, [LightMessageList])

  return (
    <div className="task-container">
        <TaskToolBar
          activityCounter={activityCounter}
          buttonFunction={OpenModal}
        />
        <div className="iframe-container">
            <iframe
                src="http://localhost:3001/#/"
                width="100%"
                height="100%"
            >

            </iframe>
        </div>
        <Modal
        show={show}
        onHide={() => setShow(false)}
        dialogClassName="modal-90w"
        aria-labelledby="example-custom-modal-styling-title"
      >
        <Modal.Header closeButton>
          <Modal.Title id="modal-header">
            Submit Session Data
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <p>
            Are you sure you are finished with this session?
          </p>
          <div>
          <Button variant="success" onClick={SubmissionHandler}>Submit</Button>{' '}
          <Button variant="danger" onClick={() => setShow(false)}>Cancel</Button>{' '}
          </div>
        </Modal.Body>
      </Modal>
    </div>
  );
}

export default App;
