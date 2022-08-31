
/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React, {useState, useEffect} from 'react';
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

    /* ------ REDUX STATE ------ */
    //Characters
    const worldCharacters = useAppSelector((state) => state.worldCharacters.worldCharacters);

  const TableFields = [
    {label:"ID", key:"id"}, 
    {label:"NAME", key:"name"},
    {label:"TYPE", key:"type"}, 
    {label:"PERSONA", key:"persona"},
    {label:"DESCRIPTION", key:"desc"}, 
  ]
  /* ------ LOCAL STATE ------ */
  const [formattedCharacterData, setFormattedCharacterData]= useState([]);

  useEffect(() => {
    let updatedCharacterData = worldCharacters.map(char=>{
      let {name, node_id, persona, desc, char_type} = char;
      let formattedId = node_id.slice((node_id.indexOf("_")+1));
      let formattedCharacter = {
        id: formattedId,
        name:name,
        type:char_type,
        persona: persona,
        desc: desc
      }
      return formattedCharacter;
    })
    setFormattedCharacterData(updatedCharacterData)
  }, [worldCharacters])

  return (
    <div>
      <GeneralTable 
        hasSearchBar={true}
        fields={TableFields} 
        data={formattedCharacterData}
      />
    </div>
  );
}

export default Characters;