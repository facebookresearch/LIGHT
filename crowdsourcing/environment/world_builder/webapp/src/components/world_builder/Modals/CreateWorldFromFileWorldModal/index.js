/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React from 'react';
/* REDUX */

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
//FORM
import Form from 'react-bootstrap/Form'
/* CUSTOM COMPONENTS */
import TextInput from "../../FormFields/TextInput";
import TextButton from "../../Buttons/TextButton"

const CreateFromFileWorldModal = ()=> {
  return (
    <div className="createworldmodal-container">
        <Modal.Header style={{backgroundColor:"lightblue"}} closeButton>
        <Modal.Title>CREATE NEW WORLD</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Row>
            <TextInput
              label={"New World Name"}
            />
          </Row>
          <Row>
            <Form.Group controlId="formFile" className="mb-3">
                <Form.Label>Upload File</Form.Label>
                <Form.Control type="file" />
            </Form.Group>
          </Row>
          <Row>
            <TextButton
                text="Create"
            />
          </Row>
        </Modal.Body>
    </div>
  );
}

export default CreateFromFileWorldModal;
