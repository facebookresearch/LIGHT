import React from "react";
import CONFIG from "../config";
import {post, useAPI } from "../utils";
import {findEmoji} from "./worldbuilding/utils"
import {Button, Intent, Spinner} from "@blueprintjs/core";
import AppToaster from "./AppToaster";

function ListWorlds ({isOpen, state, toggleOverlay}) {
    const { loading, result, reload } = useAPI(
      CONFIG,
      `/worlds/`
    );

    const deleteWorld = async (id) => {
        const res = await post(`world/delete/${id}`);
        const data = await res.json();
        console.log(data);
    };
    
    const getWorld = async (id, state) => {
    // should get back json of the loaded world, need to reconstruct it too!
    
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
        console.log(data);
        // SetDimensions, then tiles
        state.setDimensions({ ...state.dimensions, height: data.height, width: data.width, floors: data.num_floors });
        console.log(state);
        const entity_to_local = {};
        const entity_to_type = {};
        const room_chars = {};
        const room_objs = {};
        const room_tiles = {};
    
        data.rooms.forEach(room => {
            console.log(room);
            id = state.findOrAddEntity(room, "room");
            console.log(id);
            entity_to_local[room.id] = id;
            entity_to_type[room.id] = "room";
        }); 
        data.characters.forEach(character => {
            character.emoji = findEmoji(character.name);
            id = state.findOrAddEntity(character, "character");
            console.log(id);
            entity_to_local[character.id] = id;
            entity_to_type[character.id] = "character";
    
        });
        data.objects.forEach(object => {
            object.emoji = findEmoji(object.name);
            id = state.findOrAddEntity(object, "object");
            console.log(id);
            entity_to_local[object.id] = id;
            entity_to_type[object.id] = "object";
        });
        console.log("Before");
        console.log(state);
    
        data.tiles.forEach(tile => {
            let c_floor = tile.floor;
            let c_x = tile.x_coordinate;
            let c_y = tile.y_coordinate;
            room_chars[tile.room_node_id] = [];
            room_objs[tile.room_node_id] = [];
            room_tiles[tile.room_node_id] = {x: c_x, y: c_y, floor: c_floor, 
                color: tile.color, room_id: entity_to_local[tile.room_entity_id]};
        });
    
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
        console.log(room_tiles);
        console.log(room_chars);
        console.log(room_objs);
        console.log(state.entities)
        Object.keys(room_tiles).forEach(room_node => {
            console.log(room_node)
            let tile_info = room_tiles[room_node];
            const temp = {
            room: tile_info.room_id,
            characters: room_chars[room_node],
            objects: room_objs[room_node],
            color: tile_info.color
            };
            state.setTile(tile_info.x, tile_info.y, temp, tile_info.floor);
        });
        // Go through each tile object, reconstructing it (adding all walls)
        // for(... in data.tiles):
        // mapDispatch({ type: "SET_TILE", x, y, newTile, floor });
        // for(... in data.edges):
        // // 2 edges: neighbors or contains.  eitherway, need room associated with the node.
        // Go through all edges, populating the tiles with objects and neighbors 
        // which tears down the walls.
        console.log("After");
        console.log(state);
    
        AppToaster.show({
            intent: Intent.SUCCESS,
            message: "Done loading!",
        });  
        return data;
    };
    
    const data = result;
    if (!isOpen || data == undefined){
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
                            onClick={() => {toggleOverlay(!isOpen);
                                            getWorld(d.id, state); }
                                    }
                        >
                            Load
                        </Button>
                        </td>
                        <td>
                        <Button
                            intent={Intent.DANGER}
                            type="submit"
                            onClick={() => {deleteWorld(d.id); 
                                            toggleOverlay(!isOpen); 
                                            toggleOverlay(isOpen);}
                                    }
                        >
                            Delete
                        </Button>
                        </td>
                    </tr>
                    </React.Fragment>
                    ))}
            </tbody>
            </table> 
        </>); 
    }
}
  
  
export default ListWorlds;
