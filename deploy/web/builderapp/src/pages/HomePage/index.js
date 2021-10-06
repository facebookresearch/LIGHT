/* REACT */
import React, {useEffect} from 'react';
import { useHistory } from 'react-router-dom';
/* REDUX */
import {useAppDispatch, useAppSelector} from '../../app/hooks';
/* STYLES */
import './styles.css';
/* CUSTOM COMPONENTS */
import ModalContainer from "../../components/Modals";
import WorldRow from "../../components/WorldRow";
import CreateWorldButton from "../../components/Buttons/CreateWorldButton";

const HomePage = ()=> {
  let history = useHistory();
  const dummyData = [{id:1111, name: "Mars", tags:["#red", "#haunted", "#dry"]}, {id:2222, name: "Norrath", tags:["#magical", "#amazing", "#dragons"]}, {id:3333, name:"Asgard", tags:["#vikings", "#gods", "#magic"]}]
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

          />
        </div>
    </div>
       <ModalContainer/>    
    </div>
  );
}

export default HomePage;