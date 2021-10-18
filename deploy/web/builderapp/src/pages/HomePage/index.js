/* REACT */
import React, {useEffect} from 'react';
import { useHistory } from 'react-router-dom';
/* REDUX */
import {useAppDispatch, useAppSelector} from '../../app/hooks';
//ACTIONSS
import {
  setModal,
} from "../../features/modal/modal-slice";
/* STYLES */
import './styles.css';
/* CUSTOM COMPONENTS */
import ModalContainer from "../../components/Modals";
import WorldRow from "../../components/WorldRow";
import CreateWorldButton from "../../components/Buttons/CreateWorldButton";

const HomePage = ()=> {
  //REACT ROUTER
  let history = useHistory();
  //DUMMY DATA
  const dummyData = [{id:1111, name: "Mars", tags:["#red", "#haunted", "#dry"]}, {id:2222, name: "Norrath", tags:["#magical", "#amazing", "#dragons"]}, {id:3333, name:"Asgard", tags:["#vikings", "#gods", "#magic"]}]
  /* ----REDUX ACTIONS---- */
    // REDUX DISPATCH FUNCTION
    const dispatch = useAppDispatch();
    //MODALS
    const clickHandler = ()=> {
        dispatch(setModal({showModal:true, modalType:"createNewWorld"}))
    };
  return (
    <div className="homepage-container">
      <div className="homepage-label__column">
          <h1>
            Your Worlds:
          </h1>
      </div>
    <div className="homepage-world__column">
        <div className="worldcounter-container">
          <div className="worldcounter-box">
            <p style={{padding:0, margin:0}} className="worldcounter-text">
              {dummyData.length}/10 USED
            </p>
          </div>
        </div>
        {
          dummyData.map(world=><WorldRow key={world.id} world={world} clickFunction={()=>history.push(`/editworld/${world.id}`)} />)
        }
        <div className="createworldbutton-row">
          <CreateWorldButton
            clickFunction={clickHandler}
          />
        </div>
    </div>
       <ModalContainer/>    
    </div>
  );
}

export default HomePage;