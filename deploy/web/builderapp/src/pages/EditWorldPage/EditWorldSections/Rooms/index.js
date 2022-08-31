
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
/* CUSTOM COMPONENTS */
import GeneralTable from "../../../../components/Tables"

const Rooms = ()=> {

  /* ------ REDUX STATE ------ */
  //Rooms
    const worldRooms = useAppSelector((state) => state.worldRooms.worldRooms);

  const TableFields = [
    {label:"ID", key:"id"}, 
    {label:"NAME", key:"name"},
    {label:"DESCRIPTION", key:"desc"}, 
  ]
  /* ------ LOCAL STATE ------ */
  const [formattedRoomData, setFormattedRoomData]= useState([]);

  useEffect(() => {
    let updatedRoomData = worldRooms.map(room=>{
      let {name, node_id, desc} = room;
      let formattedId = node_id.slice((node_id.indexOf("_")+1));
      let formattedRoom = {
        id: formattedId,
        name:name,
        desc: desc
      }
      return formattedRoom;
    })
    setFormattedRoomData(updatedRoomData)
  }, [worldRooms])
  
  return (
    <div>
      <GeneralTable 
        hasSearchBar={true}
        fields={TableFields} 
        data={formattedRoomData}
      />
    </div>
  );
}

export default Rooms;