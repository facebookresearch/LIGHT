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
/* CUSTOM COMPONENTS */
import GeneralTable from "../../../../components/Tables/";

const Characters = ()=> {
  const DummyCharacterFields = [
    {label:"ID", key:"id"}, 
    {label:"NAME", key:"name"}, 
    {label:"Description", key:"description"}
  ]
  const DummyCharacterData = [
    {id:0, name: "Orky the Orc", description:"Smarter than your average orc."},
    {id:1, name: "Gobbles the Goblin", description:"A hungry, hungry goblin."},
    {id:2, name: "Hugh Mann", description:"Just a regular peasant trying to get by."}
  ]
  
  return (
    <div>
      <GeneralTable 
        fields={DummyCharacterFields} 
        data={DummyCharacterData}
      />
    </div>
  );
}

export default Characters;