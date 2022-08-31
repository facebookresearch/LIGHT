
/*****
 * Copyright (c) Meta Platforms, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

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
import TextButton from "../../Buttons/TextButton"

const DownloadModal = ()=> {
  return (
    <div className="downloadmodal-container">
        <Modal.Header style={{backgroundColor:"lightblue"}} className="modalheader" closeButton>
          <Modal.Title>DOWNLOAD</Modal.Title>
        </Modal.Header>
        <Modal.Body style={{display:"flex", flexDirection:"column", justifyContent:"center", alignItems:"center"}}>
          <p>Click to download this world in the default LIGHT format.  It can be edited with any text editor, used with the LIGHT OSS tools, or re-uploaded here later.</p>
          <TextButton
            text="Download"
          />
        </Modal.Body>
    </div>
  );
}

export default DownloadModal;