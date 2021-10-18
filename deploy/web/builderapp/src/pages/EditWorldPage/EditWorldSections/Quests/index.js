/* REACT */
import React from 'react';
import { useParams, useRouteMatch } from "react-router-dom";
/* REDUX */
import {useAppDispatch, useAppSelector} from '../../../../app/hooks';
/* STYLES */
import './styles.css';
/* BOOTSTRAP COMPONENTS */
//LAYOUT
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
//BUTTON
import ButtonGroup from 'react-bootstrap/ButtonGroup'
import Button from 'react-bootstrap/Button'
/* CUSTOM COMPONENTS */
import GeneralTable from "../../../../components/Tables/";

const Quests = ()=> {
  const DummyQuestsFields = [
    {label:"ID", key:"id"}, 
    {label:"NAME", key:"name"}, 
    {label:"Description", key:"description"}
  ]
  const DummyQuestsData = [
    {id:0, name: "Find the wizard keys", description:"Wizards are always losing their keys.  Help a wizard find their key."},
    {id:1, name: "Seek the Holy Grail", description:"A once and future classic, find a chalice a divine being drank from."},
    {id:2, name: "Slay a Dragon", description:"Exactly as hard as it sounds, search far and wide for a fire breathing monster and return it's head to the King."}
  ]
  
  return (
    <div>
      <GeneralTable
        fields={DummyQuestsFields} 
        data={DummyQuestsData}
      />
    </div>
  );
}

export default Quests;