/* REACT */
import React, {useState, useEffect} from 'react';
import { useParams, useRouteMatch } from "react-router-dom";
/* REDUX */
import {useAppDispatch, useAppSelector} from '../../../../app/hooks';
/* STYLES */
import './styles.css';
/* CUSTOM COMPONENTS */
import GeneralTable from "../../../../components/Tables/";

const Objects = ()=> {

    /* ------ REDUX STATE ------ */
    //Characters
    const worldObjects = useAppSelector((state) => state.worldObjects.worldObjects);

  const TableFields = [
    {label:"ID", key:"id"}, 
    {label:"NAME", key:"name"},
    {label:"DESCRIPTION", key:"desc"}, 
  ]
  /* ------ LOCAL STATE ------ */
  const [formattedObjectData, setFormattedObjectData]= useState([]);

  useEffect(() => {
    let updatedObjectData = worldObjects.map(worldObject=>{
      let {name, node_id, desc} = worldObject;
      let formattedId = node_id.slice((node_id.indexOf("_")+1));
      let formattedObject = {
        id: formattedId,
        name:name,
        desc: desc
      }
      return formattedObject;
    })
    setFormattedObjectData(updatedObjectData)
  }, [worldObjects])
    
    return (
      <div>
        <GeneralTable
          hasSearchBar={true}
          fields={TableFields} 
          data={formattedObjectData}
        />
      </div>
    );
  }

export default Objects;