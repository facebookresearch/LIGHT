/* REACT */
import React, {useEffect} from 'react';
/* REDUX */
import {useAppDispatch, useAppSelector} from '../../app/hooks';
/* STYLES */
import './styles.css';
/* CUSTOM COMPONENTS */
import WorldRow from "../../components/WorldRow"

const HomePage = ()=> {
  const dummyData = [{worldName: "Mars", tags:["#red", "#haunted", "#dry"]}, {worldName: "Norrath", tags:["#magical", "#amazing", "#dragons"]}, {worldName:"Asgard", tags:["#vikings", "#gods", "#magic"]}]
  return (
    <div className="homepage-container">
        <div className="homepage-label__column">
            <h1>
              Your Worlds:
            </h1>
        </div>
       <div className="homepage-world__column">
           {
             dummyData.map(world=><WorldRow world={world} />)
           }
       </div>

    </div>
  );
}

export default HomePage;