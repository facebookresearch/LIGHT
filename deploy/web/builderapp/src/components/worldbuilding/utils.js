import React from "react";
import {Colors, Intent} from "@blueprintjs/core";
import { cloneDeep, isEmpty, merge } from "lodash";
import equal from "fast-deep-equal";
import { emojiIndex } from "emoji-mart";
import { post} from "../../utils";
import AppToaster from "../AppToaster";

export const MAX_WIDTH = 10;
export const MAX_HEIGHT = 10;
export const MAX_FLOORS = 10;

const STARTING_WIDTH = 3;
const STARTING_HEIGHT = 3;
const STARTING_FLOORS = 1;

export const DEFAULT_EMOJI = "❓";

export const TILE_COLORS = [
  Colors.GRAY3,
  Colors.VIOLET5,
  Colors.RED5,
  Colors.SEPIA5,
  Colors.GOLD5,
  Colors.FOREST5,
  Colors.BLUE5
];

const grass = [
  "grass",
  "field",
  "plains",
  "forest",
  "land",
  "gardens",
  "meadow",
  "woods",
  "jungle",
  "swamp",
  "green"
];
const water = [
  "water",
  "lake",
  "river",
  "ocean",
  "sea",
  "pond",
  "lagoon",
  "shore",
  "blue"
];
const buildings = [
  "castle",
  "fortress",
  "church",
  "cathedral",
  "tower",
  "building",
  "cave",
  "gray",
  "grey"
];
const royal = ["king", "queen", "palace", "purple"];
const brick = ["brick", "fire", "red"];
const path = ["path", "road", "bridge", "brown"];
const farm = ["farm", "cottage", "sand", "beach", "yellow", "gold"];

/**
 * Utility function for suggesting a biome (tile color) for a given room name
 */
export function findBiome(name, current) {
  const lowName = name.toLowerCase();
  if (grass.some(biome => lowName.indexOf(biome) > -1)) {
    return Colors.FOREST5;
  }
  if (water.some(biome => lowName.indexOf(biome) > -1)) {
    return Colors.BLUE5;
  }
  if (brick.some(biome => lowName.indexOf(biome) > -1)) {
    return Colors.RED5;
  }
  if (path.some(biome => lowName.indexOf(biome) > -1)) {
    return Colors.SEPIA5;
  }
  if (farm.some(biome => lowName.indexOf(biome) > -1)) {
    return Colors.GOLD5;
  }
  if (buildings.some(biome => lowName.indexOf(biome) > -1)) {
    return Colors.GRAY3;
  }
  if (royal.some(biome => lowName.indexOf(biome) > -1)) {
    return Colors.VIOLET5;
  }
  return current;
}

/**
 * Utility function for determining whether content should be "white" or "black" on a color background
 */
export function invertColor(hex) {
  if (hex.indexOf("#") === 0) {
    hex = hex.slice(1);
  }
  // convert 3-digit hex to 6-digits.
  if (hex.length === 3) {
    hex = hex[0] + hex[0] + hex[1] + hex[1] + hex[2] + hex[2];
  }
  // invert color components
  var r = parseInt(hex.slice(0, 2), 16),
    g = parseInt(hex.slice(2, 4), 16),
    b = parseInt(hex.slice(4, 6), 16);
  // pick black/white based on intensity
  return r * 0.299 + g * 0.587 + b * 0.114 > 150 ? "#182026" : "#F5F8FA";
}

export function findEmoji(name) {
  let results = emojiIndex.search(name);
  if (results[0]) {
    return results[0].native;
  }
  const words = name.split(" ");
  for (let i = 0; i < words.length; i++) {
    let string = words[i];
    if (words[i].charAt(words[i].length - 1) === "s") {
      string = words[i].substring(0, words[i].length - 1);
    }
    results = emojiIndex.search(string);
    if (results[0]) {
      return results[0].native;
    }
  }
  return DEFAULT_EMOJI;
}

const mapReducer = (state, action) => {
  switch (action.type) {
    case "SET_MAP":
      return action.map;
    case "SET_TILE":
      return state.map((floor, floorIndex) => {
        if (floorIndex === action.floor) {
          return {
            ...floor,
            tiles: {
              ...floor.tiles,
              [`${action.x} ${action.y}`]: action.newTile
            }
          };
        } else {
          return floor;
        }
      });
    case "EDIT_FLOOR_NAME":
      return state.map((floor, floorIndex) => {
        if (floorIndex === action.floor) {
          return {
            ...floor,
            name: action.name
          };
        } else {
          return floor;
        }
      });

    default:
      return state;
  }
};

const createdEntitiesReducer = (state, action) => {
  switch (action.type) {
    case "SET_ALL":
      return action.entities;
    case "ADD_ENTITY": {
      return Object.assign({}, state, {
        [action.entityType]: {
          ...state[action.entityType],
          [state.nextID]: action.data
        },
        nextID: state.nextID + 1
      });
    }
    case "EDIT_ENTITY": {
      return merge(state, {
        [action.entityType]: { [action.id]: action.data }
      });
    }
    default:
      return state;
  }
};

/**
 * Custom hook managing map state.
 * Includes utility functions for setting state of the map.
 */
export function useWorldBuilder(upload) {
  const [dimensions, setDimensions] = React.useState(
    upload
      ? upload.data.dimensions
      : {
          height: STARTING_HEIGHT,
          width: STARTING_WIDTH,
          floors: STARTING_FLOORS
        }
  );

  // Floors and tiles kept seperate to avoid unnecessary updates on either side
  // The index key is used because the Reorder component does not pass index to children
  // Represents the map state
  // Structured as: Array(Map(name: FloorName, tiles: Map(x y': TileData), walls: Map('x1 y1|x2 y2': Wall)))
  const initialMap = upload
    ? upload.data.map
    : [{ name: "1F", tiles: {}, walls: {} }];
  const [map, mapDispatch] = React.useReducer(mapReducer, initialMap);

  // Local entity store
  const [entities, entitiesDispatch] = React.useReducer(
    createdEntitiesReducer,
    upload
      ? upload.data.entities
      : { room: {}, character: {}, object: {}, nextID: 1 }
  );

  // Floor currently being viewed in the editor
  const [currFloor, setCurrFloor] = React.useState(0);

  // make sure all floors are in the map
  React.useEffect(() => {
    const newMap = [];
    for (let f = 0; f < dimensions.floors; f++) {
      newMap.push(
        map[f] ? map[f] : { name: `${f + 1}F`, tiles: {}, walls: {} }
      );
    }
    mapDispatch({ type: "SET_MAP", map: newMap });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [dimensions]);

  // Add an entity to the local store and return its temporary id
  const addEntity = (data, entityType) => {
    const id = entities.nextID;
    entitiesDispatch({ type: "ADD_ENTITY", data, entityType });
    return id;
  };

  // Edit an entity in the local store
  const editEntity = (id, data, entityType) => {
    entitiesDispatch({ type: "EDIT_ENTITY", id, data, entityType });
  };

  // Return the id of the entity in the store, or add it to the store and return the new id
  const findOrAddEntity = (data, entityType) => {
    for (let entity in entities[entityType]) {
      if (equal(entities[entityType][entity], data)) {
        return entity;
      }
    }
    return addEntity(data, entityType);
  };

  // Change data in a specific tile on the map
  const setTile = (x, y, newTile, floor = currFloor) => {
    mapDispatch({ type: "SET_TILE", x, y, newTile, floor });
  };

  // Clear data on a tile
  const clearTile = (x, y, floor = currFloor) => {
    const newMap = cloneDeep(map);
    removeStairsTile(x, y, newMap);
    delete newMap[floor].tiles[`${x} ${y}`];
    mapDispatch({ type: "SET_MAP", map: newMap });
  };

  // Swap the position of two tiles on the current floor
  const swapTiles = (x1, y1, x2, y2) => {
    mapDispatch({
      type: "SET_MAP",
      map: map.map((floor, f) => {
        if (f === currFloor) {
          removeStairsTile(x1, y1);
          removeStairsTile(x2, y2);
          return {
            ...floor,
            tiles: {
              ...floor.tiles,
              [`${x1} ${y1}`]: floor.tiles[`${x2} ${y2}`],
              [`${x2} ${y2}`]: floor.tiles[`${x1} ${y1}`]
            }
          };
        } else {
          return floor;
        }
      })
    });
  };

  // Add a row to the top of the map on all floors
  const addRowTop = () => {
    mapDispatch({
      type: "SET_MAP",
      map: map.map(floor => {
        const tileKeys = Object.keys(floor.tiles);
        const newTiles = {};
        tileKeys.forEach(key => {
          const [x, y] = key.split(" ");
          newTiles[`${x} ${parseInt(y) + 1}`] = floor.tiles[key];
        });
        const wallKeys = Object.keys(floor.walls);
        const newWalls = {};
        wallKeys.forEach(key => {
          const [t1, t2] = key.split("|");
          const [x1, y1] = t1.split(" ");
          const [x2, y2] = t2.split(" ");
          newWalls[`${x1} ${parseInt(y1) + 1}|${x2} ${parseInt(y2) + 1}`] =
            floor.walls[key];
        });
        return { ...floor, tiles: newTiles, walls: newWalls };
      })
    });
    setDimensions({ ...dimensions, height: dimensions.height + 1 });
  };

  // Add a row to the bottom of the map on all floors
  const addRowBot = () => {
    setDimensions({ ...dimensions, height: dimensions.height + 1 });
  };

  // Add a column to the left side of the map on all floors
  const addColFront = () => {
    mapDispatch({
      type: "SET_MAP",
      map: map.map(floor => {
        const tileKeys = Object.keys(floor.tiles);
        const newTiles = {};
        tileKeys.forEach(key => {
          const [x, y] = key.split(" ");
          newTiles[`${parseInt(x) + 1} ${y}`] = floor.tiles[key];
        });
        const wallKeys = Object.keys(floor.walls);
        const newWalls = {};
        wallKeys.forEach(key => {
          const [t1, t2] = key.split("|");
          const [x1, y1] = t1.split(" ");
          const [x2, y2] = t2.split(" ");
          newWalls[`${parseInt(x1) + 1} ${y1}|${parseInt(x2) + 1} ${y2}`] =
            floor.walls[key];
        });
        return { ...floor, tiles: newTiles, walls: newWalls };
      })
    });
    setDimensions({ ...dimensions, width: dimensions.width + 1 });
  };

  // Add a column to the right side of the map on all floors
  const addColEnd = () => {
    setDimensions({ ...dimensions, width: dimensions.width + 1 });
  };

  // Add a new floor
  const addFloor = () => {
    setDimensions({ ...dimensions, floors: dimensions.floors + 1 });
  };

  // Edit the name of a floor
  const editFloorName = (newName, floor) => {
    mapDispatch({ type: "EDIT_FLOOR_NAME", name: newName, floor });
  };

  // Remove stairs from a tile
  const removeStairsTile = (x, y, baseMap = map, f = currFloor) => {
    if (baseMap[f] && baseMap[f].tiles[`${x} ${y}`]) {
      delete baseMap[f].tiles[`${x} ${y}`].stairDown;
      delete baseMap[f].tiles[`${x} ${y}`].stairUp;
    }
    if (baseMap[f - 1] && baseMap[f - 1].tiles[`${x} ${y}`]) {
      delete baseMap[f - 1].tiles[`${x} ${y}`].stairUp;
    }
    if (baseMap[f + 1] && baseMap[f + 1].tiles[`${x} ${y}`]) {
      delete baseMap[f + 1].tiles[`${x} ${y}`].stairDown;
    }
  };

  // Remove all stairs up or down from a floor
  const removeStairsFloor = (floor, stair) => {
    if (!isEmpty(floor) && !isEmpty(floor.tiles)) {
      Object.keys(floor.tiles).forEach(key => {
        if (!isEmpty(floor.tiles[key])) {
          delete floor.tiles[key][stair];
        }
      });
    }
  };

  // Delete a floor
  const deleteFloor = index => {
    const newMap = map.filter((_floor, i) => i !== index);
    removeStairsFloor(newMap[index - 1], "stairUp");
    removeStairsFloor(newMap[index], "stairDown");
    mapDispatch({ type: "SET_MAP", map: newMap });

    if (currFloor >= dimensions.floors - 1) {
      setCurrFloor(0);
    }
    setDimensions({ ...dimensions, floors: dimensions.floors - 1 });
  };

  // move a floor to a different position
  const reorderFloors = (i1, i2) => {
    const reorderedFloor = map[i1];
    const filteredMap = map.filter((_floor, i) => i !== i1);

    removeStairsFloor(reorderedFloor, "stairUp");
    removeStairsFloor(reorderedFloor, "stairDown");
    removeStairsFloor(filteredMap[i1 - 1], "stairUp");
    removeStairsFloor(filteredMap[i1], "stairDown");

    const newMap = [];
    for (let i = 0; i < dimensions.floors; i++) {
      newMap.push(
        i < i2 ? filteredMap[i] : i === i2 ? reorderedFloor : filteredMap[i - 1]
      );
    }

    removeStairsFloor(newMap[i2 - 1], "stairUp");
    removeStairsFloor(newMap[i2 + 1], "stairDown");

    mapDispatch({ type: "SET_MAP", map: newMap });

    if (currFloor === i1) {
      setCurrFloor(i2);
    }
  };

  // Get tile at specified indices, or an empty object otherwise
  const getTileAt = (x, y, f = currFloor) => {
    try {
      return map[f].tiles[`${x} ${y}`];
    } catch {
      return {};
    }
  };

  // Toggle a wall
  const toggleWall = (key, f = currFloor) => {
    if (map[f].walls[key]) {
      const newMap = cloneDeep(map);
      delete newMap[f].walls[key];
      mapDispatch({ type: "SET_MAP", map: newMap });
    } else {
      mapDispatch({
        type: "SET_MAP",
        map: map.map((floor, floorIndex) => {
          if (floorIndex === f) {
            return { ...floor, walls: { ...floor.walls, [key]: true } };
          } else {
            return floor;
          }
        })
      });
    }
  };

  const filteredMap = () => {
    const filtered = [];
    for (let i = 0; i < map.length; i++) {
      const newFloor = { name: map[i].name, walls: map[i].walls };
      const newTiles = {};
      for (let tile in map[i].tiles) {
        const [x, y] = tile.split(" ");
        if (x < dimensions.width && y < dimensions.height) {
          newTiles[tile] = map[i].tiles[tile];
        }
      }
      newFloor.tiles = newTiles;
      filtered.push(newFloor);
    }
    return filtered;
  };

  
  const postWorld = async () => {

    // can pretty much just take the dimensions and entities as is
    const dat = { 
      dimensions: cloneDeep(dimensions),
      map: {tiles: [], edges: [], },
      entities: cloneDeep(entities),
    };

    const map = filteredMap();

    // create all edge relationships and tile metadata needed
    const edges = [];
    for (let floor = 0; floor < map.length; floor++) {
      const tiles = map[floor].tiles;
      for (let coord in tiles) {
        const tile = cloneDeep(tiles[coord]);
        const [x, y] = coord.split(" ").map(i => parseInt(i));

        // Now, construct the edges - first contains
        const room = tile.room;
        tiles[coord].characters.forEach(character => {
          edges.push({src: room, dst: character, type: "contains"});
        });
        tiles[coord].objects.forEach(object => {
          edges.push({src: room, dst: object, type: "contains"})
        });

        if (tiles[coord].stairUp) {
          edges.push({
            src: room, dst: map[floor + 1].tiles[coord].room, type: 'neighbors above'
          });
        }
        if (tiles[coord].stairDown) {
          edges.push({
            src: room, dst: map[floor - 1].tiles[coord].room, type: 'neighbors below'
          });
        }
        // Ensure neighbours aren't blocked by walls
        const neighbors = [
          `${x - 1} ${y}`, `${x + 1} ${y}`, `${x} ${y - 1}`, `${x} ${y + 1}`
        ];
        const dirs = [
          'neighbors to the west', 'neighbors to the east', 'neighbors to the north', 'neighbors to the south'
        ];
        for (let index in neighbors) {
          const direction = dirs[index];
          const neighbor = neighbors[index];
          if (
            !Object.keys(map[floor].walls).some(
              wall => wall.includes(neighbor) && wall.includes(coord)
            )
          ) {
            if (!isEmpty(tiles[neighbor])) {
              edges.push({
                src: room, dst: map[floor].tiles[neighbor].room, type: direction
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
    dat.map.edges = edges

    console.log("Format of saved data: ");
    console.log(dat);
    const res = await post("world/", dat);

    AppToaster.show({
      intent: Intent.SUCCESS,
      message: "World Saved! "
    });   
  }

  // Post all edges to the API
  const postEdges = async () => {
    const store = { room: {}, character: {}, object: {} };
    const map = filteredMap();
    // Create maps of all entities being used in the world
    map.forEach(floor => {
      Object.values(floor.tiles).forEach(tile => {
        store.room[tile.room] = entities.room[tile.room];
        for (let index in tile.characters) {
          store.character[tile.characters[index]] =
            entities.character[tile.characters[index]];
        }
        for (let index in tile.objects) {
          store.object[tile.objects[index]] =
            entities.object[tile.objects[index]];
        }
      });
    });
    // Post all used entities to the API and store their returned ID for edges
    const createReqs = [].concat(
      Object.values(store.room).map(async room => {
        const res = await post("entities/room", room);
        const data = await res.json();
        room.id = data[0];
      }),
      Object.values(store.character).map(async character => {
        const res = await post("entities/character", character);
        const data = await res.json();
        character.id = data[0];
      }),
      Object.values(store.object).map(async object => {
        const res = await post("entities/object", object);
        const data = await res.json();
        object.id = data[0];
      })
    );

    await Promise.all(createReqs);

    const edgeReqs = [];
    // Create all edge requests and post all of them
    for (let floor = 0; floor < map.length; floor++) {
      const tiles = map[floor].tiles;
      for (let coord in tiles) {
        const payload = { room: -1, chars: [], objs: [], neighbors: [] };
        payload.room = store.room[tiles[coord].room].id;
        tiles[coord].characters.forEach(character => {
          payload.chars.push(store.character[character].id);
        });
        tiles[coord].objects.forEach(object => {
          payload.objs.push(store.object[object].id);
        });
        if (tiles[coord].stairUp) {
          payload.neighbors.push(
            store.room[map[floor + 1].tiles[coord].room].id
          );
        }
        if (tiles[coord].stairDown) {
          payload.neighbors.push(
            store.room[map[floor - 1].tiles[coord].room].id
          );
        }
        // Ensure neighbours aren't blocked by walls
        const [x, y] = coord.split(" ").map(i => parseInt(i));
        const neighbors = [
          `${x - 1} ${y}`,
          `${x + 1} ${y}`,
          `${x} ${y - 1}`,
          `${x} ${y + 1}`
        ];
        neighbors.forEach(neighbor => {
          if (
            !Object.keys(map[floor].walls).some(
              wall => wall.includes(neighbor) && wall.includes(coord)
            )
          ) {
            if (!isEmpty(tiles[neighbor])) {
              payload.neighbors.push(store.room[tiles[neighbor].room].id);
            }
          }
        });
        edgeReqs.push(post("edges", payload));
      }
    }
    await Promise.all(edgeReqs);
    AppToaster.show({
      intent: Intent.SUCCESS,
      message: "Successfully created all edges"
    });
  };

  const exportWorld = () => {
    const data = JSON.stringify({ dimensions, map, entities }, null, "\t");
    var element = document.createElement("a");
    element.setAttribute(
      "href",
      "data:text/plain;charset=utf-8," + encodeURIComponent(data)
    );
    element.setAttribute("download", `world-${Date.now().toString()}.json`);

    element.style.display = "none";
    document.body.appendChild(element);

    element.click();

    document.body.removeChild(element);
  };

  return {
    floorManager: {
      setCurrFloor,
      addFloor,
      deleteFloor,
      reorderFloors,
      editFloorName
    },
    currFloor,
    map,
    setTile,
    clearTile,
    swapTiles,
    getTileAt,
    toggleWall,
    dimensions,
    setDimensions,
    addRowTop,
    addRowBot,
    addColFront,
    addColEnd,
    entities,
    editEntity,
    findOrAddEntity,
    postEdges,
    exportWorld,
    postWorld,
  };
}
