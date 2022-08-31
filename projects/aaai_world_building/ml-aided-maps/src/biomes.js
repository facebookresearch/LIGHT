
/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

const biome2color = {
  Coast: "#AA9F8D",
  Lake: "#3E6695",
  Land: "#C7D2AE",
  Mountain: "#F8F8F8",
  Ocean: "#35375E",
  Snow: "#FFFFFF",
  Tundra: "#DDDCBE",
  Bare: "#BBBBBB",
  Scorched: "#999999",
  Taiga: "#CDD3BD",
  Shrubland: "#C5CBBC",
  "Temperate Desert": "#E5E7CD",
  "Temperate Rain Forest": "#AAC2AA",
  "Temperate Decidiuous Forest": "#B8C7AC",
  Grassland: "#C7D3AE",
  "Subtropical Desert": "#E7DDC9",
  "Tropical Seasonal Forest": "#B0CAA7",
  "Tropical Rain Forest": "#A1B9AA",
  River: "#0000FF"
};

const category2color = {
  Abandoned: "#AAAAAA",
  Bazaar: "#FFFF00",
  Cave: "#C0C0C0",
  Countryside: "#9ACD32",
  Desert: "#FFD700",
  Dungeon: "#800000",
  Farm: "#FFA500",
  Forest: "#008000",
  Graveyard: "#708090",
  Castle: "#808080",
  Church: "#008080",
  Cottage: "#808000",
  Palace: "#DDA0DD",
  Temple: "#FFC0CB",
  Tower: "#5555AA",
  Jungle: "#00FF00",
  Lake: "#0000FF",
  Mountain: "#DCDCDC",
  Port: "#B0C4DE",
  Shore: "#87CEFA",
  Swamp: "#556B2F",
  Tavern: "#DDAAAA",
  Town: "#D2B48C",
  Trail: "#8b5a2b",
  Wasteland: "#777777"
};

const category2color2 = {
  Abandoned: "#AAAAAA",
  Bazaar: "#FFFF00",
  Cave: "#C0C0C0",
  /**/ "city in the clouds": "",
  Countryside: "#9ACD32",
  Desert: "#FFD700",
  Dungeon: "#800000",
  Farm: "#FFA500",
  Forest: "#008000",
  /**/ "frozen tundra": "",
  Graveyard: "#708090",
  Castle: "#808080",
  Church: "#008080",
  Cottage: "#808000",
  Palace: "#DDA0DD",
  Temple: "#FFC0CB",
  Tower: "#5555AA",
  Jungle: "#00FF00",
  Lake: "#0000FF",
  /**/ "magical realm": "",
  Mountain: "#DCDCDC",
  /**/ netherworld: "",
  Port: "#B0C4DE",
  Shore: "#87CEFA",
  /**/ supernatural: "",
  Swamp: "#556B2F",
  Tavern: "#DDAAAA",
  Town: "#D2B48C",
  Trail: "#8b5a2b",
  /**/ "underwater aquapolis": "",
  Wasteland: "#777777"
};

function lookupCategoryColor(category = "") {
  if (category === null) return "";
  if (category.startsWith("Outside ")) {
    return category2color2[category.replace("Outside ", "")];
  } else if (category.startsWith("Inside ")) {
    return category2color2[category.replace("Inside ", "")];
  } else {
    return category2color2[category];
  }
}

export { biome2color, category2color, lookupCategoryColor };
