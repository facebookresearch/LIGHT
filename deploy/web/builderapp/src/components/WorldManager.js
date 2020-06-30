import React from "react";
import CONFIG from "../config";
import { post, useAPI } from "../utils";
import { findEmoji } from "./worldbuilding/utils";
import { Button, Intent, Spinner } from "@blueprintjs/core";
import AppToaster from "./AppToaster";
import { Redirect } from "react-router-dom";

function ListWorlds({ isOpen, toggleOverlay }) {
  const { loading, result, reload } = useAPI(CONFIG, `/worlds/`);
  const [upload, setUpload] = React.useState(undefined);

  const deleteWorld = async (id) => {
    const res = await post(`world/delete/${id}`);
  };

  /* Given an entity id, its type, and the local entities store, get 
        the matching emoji and associate the type with the id */
  const storeEntity = (entities, entity_id, type, entity_to_type) => {
    let entity = entities[type][entity_id];
    entity.emoji = findEmoji(entity.name);
    entity_to_type[entity_id] = type;
  };

  /* Given the tiles, go through and intialize maps with the local room it holds
        and set metadata for the tile */
  const parseTiles = (tiles, room_to_tile) => {
    tiles.forEach((tile) => {
      room_to_tile[tile.room] = {
        x: tile.x_coordinate,
        y: tile.y_coordinate,
        floor: tile.floor,
        color: tile.color,
        room: tile.room,
        characters: [],
        objects: [],
      };
    });
  };

  /* Given the edges in the form of (src, dst, type), parse the rooms which contain the objects, 
        as well as the rooms that neighbor above or below for stairs */
  const parseEdges = (edges, room_to_tile, entity_to_type) => {
    edges.forEach((edge) => {
      if (edge.type == "contains") {
        if (entity_to_type[edge.dst] == "character") {
          room_to_tile[edge.src].characters.push(edge.dst);
        } else if (entity_to_type[edge.dst] == "object") {
          room_to_tile[edge.src].objects.push(edge.dst);
        } else {
          throw "Cannot contain types other than character and object";
        }
      } else if (edge.type == "neighbors above") {
        room_to_tile[edge.src].stairUp = true;
      } else if (edge.type == "neighbors below") {
        room_to_tile[edge.src].stairDown = true;
      }
    });
  };

  /* Given the metadata for tiles, construct the format expected by the frontend which
        involves mapping x, y, and floor into the map then storing the other data */
  const constructTiles = (room_to_tile, dat_map) => {
    Object.keys(room_to_tile).forEach((room_id) => {
      let tile_info = room_to_tile[room_id];
      const temp = {
        room: tile_info.room,
        characters: tile_info.characters,
        objects: tile_info.objects,
        color: tile_info.color,
      };
      if (tile_info.stairUp) {
        temp.stairUp = true;
      } else if (tile_info.stairDown) {
        temp.stairDown = true;
      }
      dat_map[tile_info.floor].tiles[tile_info.x + " " + tile_info.y] = temp;
    });
  };

  const getWorld = async (id) => {
    AppToaster.show({
      intent: Intent.PRIMARY,
      message: "Loading your world...",
      timeout: 10000,
    });

    const res = await fetch(
      `${CONFIG.host}:${CONFIG.port}/builder/world/${id}`,
      {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      }
    );
    const data = await res.json();

    console.log("Format of loaded data");
    console.log(data);

    // Construct the 3 parts of state we need
    const dat = {
      dimensions: {
        height: data.dimensions.height,
        width: data.dimensions.width,
        floors: data.dimensions.floors,
      },
      map: [{ name: "1F", tiles: {}, walls: {} }],
      entities: data.entities,
    };

    // Add all the floors we will need to the map
    var i = 2;
    while (dat.map.length < dat.dimensions.floors) {
      dat.map.push({ name: i + "F", tiles: {}, walls: {} });
      i = i + 1;
    }

    // Maps responsible for taking the db entries to local entires
    const entity_to_type = {};
    // Associate characters, objects, and tiles with local store ids for rooms
    const room_to_tile = {};

    // Add each room, character, and object emoji as well as record the type
    Object.keys(dat.entities).forEach((dat_type) => {
      Object.keys(dat.entities[dat_type]).forEach((entity_id) => {
        storeEntity(dat.entities, entity_id, dat_type, entity_to_type);
      });
    });

    parseTiles(data.map.tiles, room_to_tile);
    parseEdges(data.map.edges, room_to_tile, entity_to_type);
    constructTiles(room_to_tile, dat.map);

    // Mission accomplished!
    AppToaster.show({
      intent: Intent.SUCCESS,
      message: "Done loading!",
    });

    console.log("Reconstructed data: ");
    console.log(dat);

    setUpload(dat);
  };

  const data = result;
  if (!isOpen) {
    return <></>;
  } else if (loading) {
    return <Spinner intent={Intent.PRIMARY} />;
  } else {
    return (
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
                    background: undefined,
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
          <Redirect
            to={{ pathname: "/world_builder", state: { data: upload } }}
          />
        )}
      </>
    );
  }
}

export default ListWorlds;
