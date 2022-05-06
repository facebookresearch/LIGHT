/* REACT */
import React from 'react';
/* REDUX */
import {useAppDispatch, useAppSelector} from '../../../app/hooks';
//ACTIONSS
import {
  setModal,
} from "../../../features/modal/modal-slice";

/* STYLES */
import './styles.css';
/* BOOTSTRAP COMPONENTS */
//LAYOUT
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
//MODAL
import Modal from 'react-bootstrap/Modal'
import ModalTitle from 'react-bootstrap/ModalTitle'
import ModalBody from 'react-bootstrap/ModalBody'
/* CUSTOM COMPONENTS */
import TextInput from "../../FormFields/TextInput";
import TextButton from "../../Buttons/TextButton"

const CreateWorldModal = ()=> {
    /* ----REDUX ACTIONS---- */
    // REDUX DISPATCH FUNCTION
    const dispatch = useAppDispatch();
    //MODALS
    const clickHandler = (creationType)=> {
        dispatch(setModal({showModal:true, modalType:creationType}))
    };
  return (
    <div className="createworldmodal-container">
        <Modal.Header style={{backgroundColor:"lightblue"}} closeButton>
        <Modal.Title>CREATE NEW WORLD</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Row>
            <Col>
              <TextButton
                text="Select Pregenerated World"
                clickFunction={()=>clickHandler("preGenWorld")}
              />
            </Col>
            <Col>
              <TextButton
                text="Generate World From File"
                clickFunction={()=>clickHandler("uploadWorld")}
              />
            </Col>
            <Col>
              <TextButton
                text="Generate World From Scratch"
                clickFunction={()=>clickHandler("fromScratchWorld")}
              />
            </Col>
          </Row>
        </Modal.Body>
    </div>
  );
}

export default CreateWorldModal;
