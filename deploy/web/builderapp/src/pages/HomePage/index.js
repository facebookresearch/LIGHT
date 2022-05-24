/* REACT */
import React, {useEffect} from 'react';
import { useHistory } from 'react-router-dom';
/* REDUX */
import {useAppDispatch, useAppSelector} from '../../app/hooks';
//ACTIONS
import {fetchWorlds} from '../../features/playerWorlds/playerworlds-slice';
import {
  setModal,
} from "../../features/modal/modal-slice";
/* STYLES */
import './styles.css';
/* CUSTOM COMPONENTS */
import ModalContainer from "../../components/Modals";
import WorldRow from "../../components/WorldRow";
import CreateWorldButton from "../../components/Buttons/CreateWorldButton";
//Dummy Data
import DummyWorlds from "../../Copy/DummyData"

const HomePage = ()=> {
  //REACT ROUTER
  let history = useHistory();
  //DUMMY DATA
  /* ----REDUX ACTIONS---- */
    // REDUX DISPATCH FUNCTION
    const dispatch = useAppDispatch();
    //REDUX STATE
    const customWorlds = useAppSelector((state) => state.playerWorlds.customWorlds);
    //MODALS
    const clickHandler = ()=> {
        dispatch(setModal({showModal:true, modalType:"createNewWorld"}))
    };
    const fetchPlayerWorlds = ()=>{
      dispatch(fetchWorlds(DummyWorlds))
    }
  /* --- LIFE CYCLE FUNCTIONS --- */
  useEffect(()=>{
    fetchPlayerWorlds()
  },[])
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
              {customWorlds.length}/10 USED
            </p>
          </div>
        </div>
        {
          customWorlds.map(world=><WorldRow key={world.id} world={world} clickFunction={()=>history.push(`/editworld/${world.id}`)} />)
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