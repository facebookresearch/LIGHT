/* REACT */
import React from 'react';
/* REDUX */
import {useAppDispatch, useAppSelector} from '../../app/hooks';
/* STYLES */
import './styles.css';
/* BOOTSTRAP COMPONENTS */
import Modal from 'react-bootstrap/Modal'
import ModalTitle from 'react-bootstrap/ModalTitle'
import ModalBody from 'react-bootstrap/ModalBody'
/* CUSTOM COMPONENTS */

const CopyModal = ()=> {
  return (
    <div className="copymodal-container">
        <Modal.Header closeButton>
          <Modal.Title>COPY</Modal.Title>
        </Modal.Header>
        <Modal.Body>This allows you to make a copy of your world to edit.</Modal.Body>
    </div>
  );
}

export default CopyModal;