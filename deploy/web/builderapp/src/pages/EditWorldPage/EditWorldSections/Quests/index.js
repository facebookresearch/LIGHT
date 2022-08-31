
/*****
 * Copyright (c) Meta Platforms, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React, {useState, useEffect}  from 'react';
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
  /* ------ REDUX STATE ------ */
  //Quests
  const worldQuests = useAppSelector((state) => state.worldQuests.worldQuests);

  const TableFields = [
    {label:"ID", key:"id"}, 
    {label:"NAME", key:"name"},
  ]
  /* ------ LOCAL STATE ------ */
  const [formattedQuestData, setFormattedQuestData]= useState([]);

  useEffect(() => {
    let updatedRoomData = worldQuests.map(quest=>{
      let {name, node_id} = quest;
      let formattedId = node_id.slice((node_id.indexOf("_")+1));
      let formattedQuest = {
        id: formattedId,
        name:name,
      }
      return formattedQuest;
    })
    setFormattedQuestData(updatedRoomData)
  }, [worldQuests])
  return (
    <div>
      <GeneralTable
        hasSearchBar={true}
        fields={TableFields} 
        data={formattedQuestData}
      />
    </div>
  );
}

export default Quests;