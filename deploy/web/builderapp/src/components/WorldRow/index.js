/* REACT */
import React from "react";
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
                <BsDownload />
                <FaShare />
                <IoDuplicateOutline />
                <AiFillDelete color="red" />
            </div>
        </div>
    );
};

export default WorldRow;