/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React from 'react';
/* REDUX */
import {useAppDispatch, useAppSelector} from '../../../app/hooks';
/* STYLES */
import './styles.css';
/* BOOTSTRAP COMPONENTS */
import Modal from 'react-bootstrap/Modal'
import ModalTitle from 'react-bootstrap/ModalTitle'
import ModalBody from 'react-bootstrap/ModalBody'
/* CUSTOM COMPONENTS */

const ShareModal = ()=> {
    /* ----REDUX STATE---- */
    const selectedWorld = useAppSelector((state) => state.playerWorlds.selectedWorld);
  return (
    <div className="sharemodal-container">
        <Modal.Header style={{backgroundColor:"lightblue"}} closeButton>
          <Modal.Title>{`Share ${selectedWorld.name}`}</Modal.Title>
        </Modal.Header>
        <Modal.Body>Click below to generate a link to share with friends such that you can all enter the same world. This link will expire if nobdy usees the world for 30 minutes.</Modal.Body>
    </div>
  );
}

export default ShareModal;