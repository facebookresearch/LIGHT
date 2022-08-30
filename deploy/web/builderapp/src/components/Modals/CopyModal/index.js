
/*****
 * Copyright (c) Meta Platforms, Inc. and its affiliates.
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
import TextInput from "../../FormFields/TextInput";
import TextButton from "../../Buttons/TextButton"

const CopyModal = ()=> {
  /* ----REDUX STATE---- */
  const selectedWorld = useAppSelector((state) => state.playerWorlds.selectedWorld);
  return (
    <div className="copymodal-container">
        <Modal.Header style={{backgroundColor:"lightblue"}} closeButton>
          <Modal.Title>{`Copy ${selectedWorld.name}`}</Modal.Title>
        </Modal.Header>
        <Modal.Body style={{display:"flex", flexDirection:"column", justifyContent:"center", alignItems:"center"}}>
          <p>This allows you to make a copy of your world to edit.</p>
          <p>Provide a name to duplicate this world into.</p>
          <div style={{width:"30%", display:"flex", flexDirection:"column", justifyContent:"center", alignItems:"center"}}>
              <TextInput 
                label={"New World Name"}
              />
              <TextButton 
                text="COPY"
                clickFunction={()=>{}}
              />
          </div>
        </Modal.Body>
    </div>
  );
}

export default CopyModal;