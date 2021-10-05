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

const DownloadModal = ()=> {
  return (
    <div className="downloadmodal-container">
        <Modal.Header closeButton>
          <Modal.Title>DOWNLOAD</Modal.Title>
        </Modal.Header>
        <Modal.Body>Click to download this world in the default LIGHT format.  It can be edited with any text editor, used with the LIGHT OSS tools, or re-uploaded here later.</Modal.Body>
    </div>
  );
}

export default DownloadModal;