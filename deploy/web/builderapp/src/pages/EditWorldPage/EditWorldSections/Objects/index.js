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

const Objects = ()=> {
    const DummyObjectsFields = [
      {label:"ID", key:"id"}, 
      {label:"NAME", key:"name"}, 
      {label:"Description", key:"description"}
    ]
    const DummyObjectsData = [
      {id:0, name: "A bone club", description:"A crude weapon made from a large bone."},
      {id:1, name: "A plate helmet", description:"A shiny piece of armor for one's head."},
      {id:2, name: "A bucket", description:"An empty vessel that could be used to carry any number of things."}
    ]
    
    return (
      <div>
        <GeneralTable
          hasSearchBar={true}
          fields={DummyObjectsFields} 
          data={DummyObjectsData}
        />
      </div>
    );
  }

export default Objects;