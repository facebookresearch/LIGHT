import React from "react";
import CONFIG from "../config";
import {post, useAPI } from "../utils";
import {findEmoji} from "./worldbuilding/utils"
import {Button, Intent, Spinner} from "@blueprintjs/core";
import AppToaster from "./AppToaster";
import { Redirect } from "react-router-dom";

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

        // Construct the 3 parts of state we need
        const dat = { 
            dimensions: {height: data.height, width: data.width, floors: data.num_floors},
            map: [{name: "1F", tiles: {}, walls: {}}],
            entities: {room: {}, character: {}, object: {}, nextID: 1},
        };

        // Add all the floors we will need to the map
        var i = 2;
        while (dat.map.length < data.num_floors){
            dat.map.push({name: i + "F", tiles: {}, walls: {}});
            i = i + 1;
        }

        // Maps responsible for taking the db entries to local entires
        const entity_to_local = {};
        const entity_to_type = {};
        const room_chars = {};
        const room_objs = {};
        const room_tiles = {};
    
        // Add each room, character, and object to the data store
        data.rooms.forEach(room => {
            id = dat.entities.nextID;
            room.emoji = findEmoji(room.name);
            dat.entities.room[dat.entities.nextID] = room;
            dat.entities.nextID = dat.entities.nextID + 1;
            console.log(id);
            entity_to_local[room.id] = id;
            entity_to_type[room.id] = "room";
        }); 

        data.characters.forEach(character => {
            id = dat.entities.nextID;
            character.emoji = findEmoji(character.name);
            dat.entities.character[dat.entities.nextID] = character;
            dat.entities.nextID = dat.entities.nextID + 1;
            console.log(id);
            entity_to_local[character.id] = id;
            entity_to_type[character.id] = "character";
        });

        data.objects.forEach(object => {
            id = dat.entities.nextID;
            object.emoji = findEmoji(object.name);
            dat.entities.object[dat.entities.nextID] = object;
            dat.entities.nextID = dat.entities.nextID + 1;
            console.log(id);
            entity_to_local[object.id] = id;
            entity_to_type[object.id] = "object";
        });

        // Go through recording the room node needed for each tile
        data.tiles.forEach(tile => {
            let c_floor = tile.floor;
            let c_x = tile.x_coordinate;
            let c_y = tile.y_coordinate;
            room_chars[tile.room_node_id] = [];
            room_objs[tile.room_node_id] = [];
            room_tiles[tile.room_node_id] = {x: c_x, y: c_y, floor: c_floor, 
                color: tile.color, room_id: entity_to_local[tile.room_entity_id]};
        });
    
        // Associate each entity with room it is in (TODO: Add walls/stair logic)
        data.edges.forEach(edge => {
            console.log(edge);
            if (edge.edge_type == "contains"){
                if(entity_to_type[edge.dst_entity_id] == "character"){
                    room_chars[edge.src_id].push(entity_to_local[edge.dst_entity_id]);
                }else if (entity_to_type[edge.dst_entity_id] == "object"){
                    room_objs[edge.src_id].push(entity_to_local[edge.dst_entity_id]);
                }else{
                    console.log("This should not be happening...");
                }
            }
        });

        // Finally, add each tile to the map!
        Object.keys(room_tiles).forEach(room_node => {
            console.log(room_node)
            let tile_info = room_tiles[room_node];
            const temp = {
                room: tile_info.room_id,
                characters: room_chars[room_node],
                objects: room_objs[room_node],
                color: tile_info.color
            };
            dat.map[tile_info.floor].tiles[tile_info.x + " " + tile_info.y] = temp;
        });

        // Mission accomplished!
        AppToaster.show({
            intent: Intent.SUCCESS,
            message: "Done loading!",
        });  
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
