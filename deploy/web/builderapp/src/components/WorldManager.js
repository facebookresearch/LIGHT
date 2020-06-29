import React from "react";
import CONFIG from "../config";
import {post, useAPI } from "../utils";
import {findEmoji} from "./worldbuilding/utils"
import {Button, Intent, Spinner} from "@blueprintjs/core";
import AppToaster from "./AppToaster";
import { Redirect } from "react-router-dom";
import cloneDeep from "lodash";

function ListWorlds ({isOpen, toggleOverlay}) {
    const { loading, result, reload } = useAPI(
      CONFIG,
      `/worlds/`
    );
    const [upload, setUpload] = React.useState(undefined);

    const deleteWorld = async (id) => {
        const res = await post(`world/delete/${id}`);
    };

    const getWorld = async (id) => {    
        
        AppToaster.show({
            intent: Intent.PRIMARY,
            message: "Loading your world...",
            timeout: 10000
        });  

        const res = await fetch(`${CONFIG.host}:${CONFIG.port}/builder/world/${id}`, {
            method: "GET",
            headers: {
            "Content-Type": "application/json",
            }});
        const data = await res.json();
        console.log(data)
        // Construct the 3 parts of state we need
        const dat = { 
            dimensions: {height: data.dimensions.height, width: data.dimensions.width, 
                floors: data.dimensions.floors},
            map: [{name: "1F", tiles: {}, walls: {}}],
            entities: data.entities,
        };
        console.log(dat)
        // Add all the floors we will need to the map
        var i = 2;
        while (dat.map.length < data.num_floors){
            dat.map.push({name: i + "F", tiles: {}, walls: {}});
            i = i + 1;
        }

        // Maps responsible for taking the db entries to local entires
        const entity_to_type = {};
        const room_chars = {};
        const room_objs = {};
        const room_tiles = {};
    
        // Add each room, character, and object emoji
        Object.keys(dat.entities.room).forEach(room_local_id => {
            let room = dat.entities.room[room_local_id];
            room.emoji = findEmoji(room.name);
            entity_to_type[room_local_id] = "room";
        }); 

        Object.keys(dat.entities.character).forEach(char_local_id => {
            let character = dat.entities.character[char_local_id];
            character.emoji = findEmoji(character.name);
            entity_to_type[char_local_id] = "character";
        });

        Object.keys(dat.entities.object).forEach(obj_local_id => {
            let object = dat.entities.object[obj_local_id];
            object.emoji = findEmoji(object.name);
            entity_to_type[obj_local_id] = "object";
        });

        // Go through recording the room node needed for each tile
        data.map.tiles.forEach(tile => {
            let c_floor = tile.floor;
            let c_x = tile.x_coordinate;
            let c_y = tile.y_coordinate;
            room_chars[tile.room] = [];
            room_objs[tile.room] = [];
            room_tiles[tile.room] = {x: c_x, y: c_y, floor: c_floor, 
                color: tile.color, room: tile.room};
        });
    
        // Associate each entity with room it is in (TODO: Add walls/stair logic)
        data.map.edges.forEach(edge => {
            console.log(edge);
            if (edge.type == "contains"){
                if(entity_to_type[edge.dst] == "character"){
                    room_chars[edge.src].push(edge.dst);
                }else if (entity_to_type[edge.dst] == "object"){
                    room_objs[edge.src].push(edge.dst);
                }else{
                    console.log("This should not be happening...");
                }
            }else if (edge.type == "neighbors above"){
                room_tiles[edge.src].stairUp = true; 
            }else if (edge.type == "neighbors below"){
                room_tiles[edge.src].stairDown = true;
            }
        });

        // Finally, add each tile to the map!
        Object.keys(room_tiles).forEach(room_node => {
            let tile_info = room_tiles[room_node];
            const temp = {
                room: tile_info.room,
                characters: room_chars[room_node],
                objects: room_objs[room_node],
                color: tile_info.color
            };
            if (tile_info.stairUp){
                temp.stairUp = true;
            }else if (tile_info.stairDown){
                temp.stairDown = true;
            }
            dat.map[tile_info.floor].tiles[tile_info.x + " " + tile_info.y] = temp;
        });

        // Mission accomplished!
        AppToaster.show({
            intent: Intent.SUCCESS,
            message: "Done loading!",
        });  
        console.log(dat);
        setUpload(dat)
    };

    const data = result;
    if (!isOpen){
        return <></>;
    }else if (loading){
        return <Spinner intent={Intent.PRIMARY} />;
    }else{
        return(
        <>
            <table
                data-testid="world-review"
                style={{ width: "100%" }}
                className="bp3-html-table bp3-html-table-condensed bp3-interactive"
            >
            <thead>
            <tr>
                <th>World ID</th>
                <th>World Name</th>
                <th>Load</th>
                <th>Delete</th>
            </tr>
            </thead>
            <tbody>
                {data.map((d) => (
                    <React.Fragment key={d.id}>
                    <tr
                        data-testid="tr-review"
                        style={{
                        background: undefined
                        }}
                    >
                        <td>{d.id}</td>
                        <td>
                        <strong>{d.name}</strong>
                        </td>
                        <td>
                        <Button
                            intent={Intent.SUCCESS}
                            type="submit"
                            onClick={() => getWorld(d.id)}
                        >
                            Load
                        </Button>
                        </td>
                        <td>
                        <Button
                            intent={Intent.DANGER}
                            type="submit"
                            onClick={() => deleteWorld(d.id)}
                        >
                            Delete
                        </Button>
                        </td>
                    </tr>
                    </React.Fragment>
                    ))}
            </tbody>
            </table> 
            {upload && (
                <Redirect to={{ pathname: "/world_builder", state: { data: upload } }} />
            )}
        </>); 
    }
}
  
export default ListWorlds;
