
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
import TextButton from "../../Buttons/TextButton"

const DeleteModal = ()=> {
  /* ----REDUX STATE---- */
  const selectedWorld = useAppSelector((state) => state.playerWorlds.selectedWorld);
  return (
    <div className="deletemodal-container">
        <Modal.Header style={{backgroundColor:"lightblue"}} closeButton>
        <Modal.Title>{`Delete ${selectedWorld.name}`}</Modal.Title>
        </Modal.Header>
        <Modal.Body style={{display:"flex", flexDirection:"column", justifyContent:"center", alignItems:"center"}}>
          <p>
            You can delete this world to make space for new worlds.
          </p>
          <p>
            Warning, this action CANNOT be reversed.  Download the world first if you may want to use it later.
          </p>
          <div style={{width:"30%", display:"flex", flexDirection:"column", justifyContent:"center", alignItems:"center"}}>
          <TextButton 
                text="DELETE"
                clickFunction={()=>{}}
              />
          </div>
        </Modal.Body>
    </div>
  );
}

export default DeleteModal;