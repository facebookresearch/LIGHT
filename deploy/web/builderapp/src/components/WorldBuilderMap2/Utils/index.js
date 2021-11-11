import React from "react";
import { Colors } from "@blueprintjs/core";
import { cloneDeep, isEmpty, merge } from "lodash";
import equal from "fast-deep-equal";
import { emojiIndex } from "emoji-mart";

import Tile from "../Tile"

export const MAX_WIDTH = 10;
export const MAX_HEIGHT = 10;
export const MAX_FLOORS = 10;

const SIZE = 150;
const MARGIN = 24;

const STARTING_WIDTH = 5;
const STARTING_HEIGHT = 5;
const STARTING_FLOORS = 1;

export const DEFAULT_EMOJI = "❓";

export const TILE_COLORS = [
  Colors.GRAY3,
  Colors.VIOLET5,
  Colors.RED5,
  Colors.SEPIA5,
  Colors.GOLD5,
  Colors.FOREST5,
  Colors.BLUE5,
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
  "green",
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
  "blue",
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
  "grey",
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
    if (grass.some((biome) => lowName.indexOf(biome) > -1)) {
      return Colors.FOREST5;
    }
    if (water.some((biome) => lowName.indexOf(biome) > -1)) {
      return Colors.BLUE5;
    }
    if (brick.some((biome) => lowName.indexOf(biome) > -1)) {
      return Colors.RED5;
    }
    if (path.some((biome) => lowName.indexOf(biome) > -1)) {
      return Colors.SEPIA5;
    }
    if (farm.some((biome) => lowName.indexOf(biome) > -1)) {
      return Colors.GOLD5;
    }
    if (buildings.some((biome) => lowName.indexOf(biome) > -1)) {
      return Colors.GRAY3;
    }
    if (royal.some((biome) => lowName.indexOf(biome) > -1)) {
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

// Sets "edges" of world map using the most extreme x and y values on the matrix 
export function calculateMapBorders(roomNodes){
    let borders = {
        top: 2,
        bottom: -2,
        left: -2,
        right: 2
    }
    roomNodes.map((roomNode)=>{
        let {grid_location} = roomNode;
        let x = grid_location[0]
        let y = grid_location[1]
        borders.top = borders.top > y ? borders.top : y;
        borders.bottom = borders.top < y ? borders.top : y;
        borders.right = borders.right > x ? borders.top : x;
        borders.left = borders.left < x ? borders.left : x;
    })
    return borders;
}
