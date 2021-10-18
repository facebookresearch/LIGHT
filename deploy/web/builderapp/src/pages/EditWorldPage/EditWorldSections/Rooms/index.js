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
import GeneralTable from "../../../../components/Tables"

const Rooms = ()=> {
  const DummyRoomFields = [
    {label:"ID", key:"id"}, 
    {label:"NAME", key:"name"}, 
    {label:"Description", key:"description"}
  ]
  const DummyRoomData = [
    {id:0, name: "Dungeon", description:"A dark, cold prison."},
    {id:1, name: "Forest", description:"A wild maze of trees."},
    {id:2, name: "Village", description:"A quiet village."}
  ]
  
  return (
    <div>
      <GeneralTable 
        fields={DummyRoomFields} 
        data={DummyRoomData}
      />
    </div>
  );
}

export default Rooms;