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

const DownloadModal = ()=> {
  return (
    <div className="downloadmodal-container">
        <Modal.Header style={{backgroundColor:"lightblue"}} className="modalheader" closeButton>
          <Modal.Title>DOWNLOAD</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <p>Click to download this world in the default LIGHT format.  It can be edited with any text editor, used with the LIGHT OSS tools, or re-uploaded here later.</p>

        </Modal.Body>
    </div>
  );
}

export default DownloadModal;