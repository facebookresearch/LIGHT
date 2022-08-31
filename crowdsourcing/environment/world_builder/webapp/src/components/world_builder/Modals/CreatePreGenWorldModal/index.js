
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
/* CUSTOM COMPONENTS */
import TextInput from "../../FormFields/TextInput";
import TextButton from "../../Buttons/TextButton"

const CreatePreGenWorldModal = ()=> {
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
            <Col>
              <TextButton
                text="Select Pregenerated World"
              />
            </Col>
            <Col>
              <TextButton
                text="Generate World From File"
              />
            </Col>
            <Col>
              <TextButton
                text="Generate World From Scratch"
              />
            </Col>
          </Row>
        </Modal.Body>
    </div>
  );
}

export default CreatePreGenWorldModal;
