
/*****
 * Copyright (c) Meta Platforms, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React from "react";
/* REDUX */
import {useAppDispatch, useAppSelector} from '../../app/hooks';
import {
  setModal,
} from "../../features/modal/modal-slice";
import { 
    selectWorld 
} from "../../features/playerWorlds/playerworlds-slice.ts";
/* STYLES */
import "./styles.css";
/* ICONS */
import { BsDownload } from 'react-icons/bs';
import { FaShare } from 'react-icons/fa';
import { IoDuplicateOutline } from 'react-icons/io5';
import { AiFillDelete } from 'react-icons/ai';
/* CUSTOM COMPONENTS */
import TextButton from "../Buttons/TextButton"


//WorldRow - Row for custom worlds
const WorldRow = ({
    world,
    clickFunction
 }) => {
    /* ----REDUX ACTIONS---- */
    // REDUX DISPATCH FUNCTION
    const dispatch = useAppDispatch();
    //MODALS
    const openModal = (modalType, clickedWorld)=> {
        let {id, name} = clickedWorld;
        dispatch(selectWorld({id:id, name:name}))
        dispatch(setModal({showModal:true, modalType:modalType}))
    };
    const {name, tags} = world;
    return (
        <div className="worldrow-container">
            <div className="worldrow-tags__container" >
                {
                    tags.map((tag)=><span className="worldrow-tags__text">{tag}</span>)
                }
            </div>
            <div className="worldrow-name__container" >
                <TextButton 
                    text={name} 
                    clickFunction={clickFunction}
                />
            </div>
            <div className="worldrow-icons__container" >
                <BsDownload className="worldrow-icon download" onClick={()=>openModal("download", world)}  />
                <FaShare className="worldrow-icon share"  onClick={()=>openModal("share", world)}  />
                <IoDuplicateOutline className="worldrow-icon duplicate"  onClick={()=>openModal("copy", world)} />
                <AiFillDelete className="worldrow-icon delete"  onClick={()=>openModal("delete", world)} color="red" />
            </div>
        </div>
    );
};

export default WorldRow;