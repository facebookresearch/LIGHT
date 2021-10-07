/* REACT */
import React from 'react';
/* REDUX */

/* STYLES */
import './styles.css';
/* BOOTSTRAP COMPONENTS */
import Modal from 'react-bootstrap/Modal'
import ModalTitle from 'react-bootstrap/ModalTitle'
import ModalBody from 'react-bootstrap/ModalBody'
/* CUSTOM COMPONENTS */

const CreateWorldModal = ()=> {
  return (
    <div className="createworldmodal-container">
        <Modal.Header closeButton>
        <Modal.Title>NEW WORLD</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          
          <input />
          
        </Modal.Body>
    </div>
  );
}

export default CreateWorldModal;