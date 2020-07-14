import React from "react";
import classNames from "classnames";
import CONFIG from "../config";
import { post, useAPI } from "../utils";
import { findEmoji } from "./worldbuilding/utils";
import AppToaster from "./AppToaster";
import { Redirect } from "react-router-dom";
import { Button, Classes, Intent, Overlay, Spinner } from "@blueprintjs/core";
import { cloneDeep, isEmpty } from "lodash";
import { EDGE_TYPES } from "./EdgeTypes";

function ListWorldsOverlay({ isOverlayOpen, setIsOverlayOpen }) {
  const classes = classNames(Classes.CARD, Classes.ELEVATION_4);
  return (
    <>
      <div>
        <Overlay
          className={Classes.OVERLAY_SCROLL_CONTAINER}
          isOpen={isOverlayOpen}
          onClose={() => setIsOverlayOpen(!isOverlayOpen)}
        >
          <div className={classes}>
            <ListWorlds
              isOpen={isOverlayOpen}
              setIsOverlayOpen={setIsOverlayOpen}
            />
            <Button
              intent={Intent.DANGER}
              onClick={() => setIsOverlayOpen(!isOverlayOpen)}
              style={{ margin: "10px" }}
            >
              Close
            </Button>
          </div>
        </Overlay>
      </div>
    </>
  );
}

function ListWorlds({ isOpen, setIsOverlayOpen }) {
  const { loading, result, reload } = useAPI(CONFIG, `/worlds/`);
  const [upload, setUpload] = React.useState(undefined);

  const deleteWorld = async (id) => {
    const res = await fetch(`${CONFIG.host}:${CONFIG.port}/builder/world/delete/${id}`, {
      method: "DELETE",
    });
  };

  /* Given an entity id, its type, and the local entities store, get 
        the matching emoji and associate the type with the id */
  const storeEntity = (entities, entityId, type, entityToType) => {
    let entity = entities[type][entityId];
    entity.emoji = findEmoji(entity.name);
    entityToType[entityId] = type;
  };

  /* Given the tiles, go through and intialize maps with the local room it holds
        and set metadata for the tile */
  const parseTiles = (tiles, roomToTile) => {
    tiles.forEach((tile) => {
      roomToTile[tile.room] = {
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
  const parseEdges = (edges, roomToTile, entityToType) => {
    edges.forEach((edge) => {
      if (edge.type === EDGE_TYPES.CONTAINS) {
        if (entityToType[edge.dst] === "character") {
          roomToTile[edge.src].characters.push(edge.dst);
        } else if (entityToType[edge.dst] === "object") {
          roomToTile[edge.src].objects.push(edge.dst);
        } else {
          throw "Cannot contain types other than character and object";
        }
      } else if (edge.type === EDGE_TYPES.NEIGHBORS_ABOVE) {
        roomToTile[edge.src].stairUp = true;
      } else if (edge.type === EDGE_TYPES.NEIGHBORS_BELOW) {
        roomToTile[edge.src].stairDown = true;
      }
    });
  };

  /* Given the metadata for tiles, construct the format expected by the frontend which
        involves mapping x, y, and floor into the map then storing the other data */
  const constructTiles = (roomToTile, datMap) => {
    Object.keys(roomToTile).forEach((roomId) => {
      let tileInfo = roomToTile[roomId];
      const temp = {
        room: tileInfo.room,
        characters: tileInfo.characters,
        objects: tileInfo.objects,
        color: tileInfo.color,
      };
      if (tileInfo.stairUp) {
        temp.stairUp = true;
      } else if (tileInfo.stairDown) {
        temp.stairDown = true;
      }
      datMap[tileInfo.floor].tiles[tileInfo.x + " " + tileInfo.y] = temp;
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

    // Construct the 3 parts of state we need
    const dat = {
      dimensions: {
        name: data.dimensions.name,
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
    const entityToType = {};
    // Associate characters, objects, and tiles with local store ids for rooms
    const roomToTile = {};

    // Add each room, character, and object emoji as well as record the type
    Object.keys(dat.entities).forEach((datType) => {
      Object.keys(dat.entities[datType]).forEach((entityId) => {
        storeEntity(dat.entities, entityId, datType, entityToType);
      });
    });

    parseTiles(data.map.tiles, roomToTile);
    parseEdges(data.map.edges, roomToTile, entityToType);
    constructTiles(roomToTile, dat.map);

    // Mission accomplished!
    AppToaster.show({
      intent: Intent.SUCCESS,
      message: "Done loading!",
    });

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
              <th>Height</th>
              <th>Width</th>
              <th>Number of Floors</th>
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
                  <td>{d.height}</td>
                  <td>{d.width}</td>
                  <td>{d.num_floors}</td>
                  <td>
                    <Button
                      intent={Intent.PRIMARY}
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
/* Functions should:
  1. Save the world - regardless of if it has been saved or not!
  2. Pass the id to the game (hit the POST game/new) endpoint
    - Should we include cool naming as jason suggested?  i.e url param for name?
    - get url param from response
  3. Surface the url param/link on the page
      * might be judicious to impose some limit on number of launches a user gets per session
*/
export async function launchWorld(state){
  // TODO: See above
  const world_id = await postWorld(state);

  const formBody = [];
  const encodedKey = encodeURIComponent("world_id");
  const encodedValue = encodeURIComponent(world_id);
  formBody.push(encodedKey + "=" + encodedValue);

  const res = await fetch(`${CONFIG.host}:${CONFIG.port}/game/new/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: formBody.join("&"),
  });
  const data = await res.json();
  console.log(data)
  // New component here?  or just return link and surface somewhere else?
  return data;
}

export async function postWorld(state) {
  // can pretty much just take the dimensions and entities as is
  const dat = {
    dimensions: cloneDeep(state.dimensions),
    map: { tiles: [], edges: [] },
    entities: cloneDeep(state.entities),
  };
  // Add name and id field (blank rn)
  dat.dimensions["id"] = null;
  const map = state.filteredMap();

  // create all edge relationships and tile metadata needed
  const edges = [];
  for (let floor = 0; floor < map.length; floor++) {
    const tiles = map[floor].tiles;
    for (let coord in tiles) {
      const tile = cloneDeep(tiles[coord]);
      const [x, y] = coord.split(" ").map((i) => parseInt(i));

      // Now, construct the edges - first contains
      const room = tile.room;
      tiles[coord].characters.forEach((character) => {
        edges.push({ src: room, dst: character, type: EDGE_TYPES.CONTAINS });
      });
      tiles[coord].objects.forEach((object) => {
        edges.push({ src: room, dst: object, type: EDGE_TYPES.CONTAINS });
      });

      if (tiles[coord].stairUp) {
        delete tile.stairUp;
        edges.push({
          src: room,
          dst: map[floor + 1].tiles[coord].room,
          type: EDGE_TYPES.NEIGHBORS_ABOVE,
        });
      }
      if (tiles[coord].stairDown) {
        delete tile.stairDown;
        edges.push({
          src: room,
          dst: map[floor - 1].tiles[coord].room,
          type: EDGE_TYPES.NEIGHBORS_BELOW,
        });
      }
      // Ensure neighbours aren't blocked by walls
      const neighbors = [
        `${x - 1} ${y}`,
        `${x + 1} ${y}`,
        `${x} ${y - 1}`,
        `${x} ${y + 1}`,
      ];
      const dirs = [
        EDGE_TYPES.NEIGHBORS_WEST,
        EDGE_TYPES.NEIGHBORS_EAST,
        EDGE_TYPES.NEIGHBORS_NORTH,
        EDGE_TYPES.NEIGHBORS_SOUTH,
      ];
      for (let index in neighbors) {
        const direction = dirs[index];
        const neighbor = neighbors[index];
        if (
          !Object.keys(map[floor].walls).some(
            (wall) => wall.includes(neighbor) && wall.includes(coord)
          )
        ) {
          if (!isEmpty(tiles[neighbor])) {
            edges.push({
              src: room,
              dst: map[floor].tiles[neighbor].room,
              type: direction,
            });
          }
        }
      }

      // Modify tile object to expected format and push
      tile["x_coordinate"] = x;
      tile["y_coordinate"] = y;
      tile["floor"] = floor;
      delete tile.characters;
      delete tile.objects;
      dat.map.tiles.push(tile);
    }
  }
  // send it to the saving format!
  dat.map.edges = edges;
  const res = await post("world/", dat);
  const resData = await res.json();
  AppToaster.show({
    intent: Intent.SUCCESS,
    message: "World Saved! ",
  });
  // Return the id
  return resData;
}

export default ListWorldsOverlay;
