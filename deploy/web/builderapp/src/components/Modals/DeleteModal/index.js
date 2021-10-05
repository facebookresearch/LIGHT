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

const DeleteModal = ()=> {
  return (
    <div className="deletemodal-container">
        <Modal.Header closeButton>
        <Modal.Title>DELETE</Modal.Title>
        </Modal.Header>
        <Modal.Body>You can delete this world to make space for new worlds</Modal.Body>
    </div>
  );
}

export default DeleteModal;