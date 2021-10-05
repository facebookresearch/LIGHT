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

const ShareModal = ()=> {
  return (
    <div className="sharemodal-container">
        <Modal.Header closeButton>
          <Modal.Title>SHARE</Modal.Title>
        </Modal.Header>
        <Modal.Body>Click below to generate a link to share with friends such that you can all enter the same world. This link will expire if nobdy usees the world for 30 minutes.</Modal.Body>
    </div>
  );
}

export default ShareModal;