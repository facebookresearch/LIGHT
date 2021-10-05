/* REACT */
import React from "react";
/* REDUX */
import {useAppDispatch, useAppSelector} from '../../app/hooks';
import {
  setModal,
} from "../../features/modal/modal-slice";
/* STYLES */
import "./styles.css";
/* ICONS */
import { BsDownload } from 'react-icons/bs';
import { FaShare } from 'react-icons/fa';
import { IoDuplicateOutline } from 'react-icons/io5';
import { AiFillDelete } from 'react-icons/ai';

//WorldRow - Row for custom worlds
const WorldRow = ({
    world
 }) => {
    /* ----REDUX ACTIONS---- */
    // REDUX DISPATCH FUNCTION
    const dispatch = useAppDispatch();
    //MODALS
    const openModal = (modalType)=> dispatch(setModal({showModal:true, modalType:modalType}));
    const {name, tags} = world;
    return (
        <div className="worldrow-container">
            <div className="worldrow-tags__container" >
                {
                    tags.map((tag)=><span className="worldrow-tags__text">{tag}</span>)
                }
            </div>
            <div className="worldrow-name__container" >
                <input className="worldrow-name__text" value={name} />
            </div>
            <div className="worldrow-icons__container" >
                <BsDownload onClick={()=>openModal("download")}  />
                <FaShare onClick={()=>openModal("share")}  />
                <IoDuplicateOutline onClick={()=>openModal("duplicate")} />
                <AiFillDelete onClick={()=>openModal("delete")} color="red" />
            </div>
        </div>
    );
};

export default WorldRow;