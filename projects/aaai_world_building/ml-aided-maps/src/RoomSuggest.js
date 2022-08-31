/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react";
import { Suggest } from "@blueprintjs/select";
import { MenuItem } from "@blueprintjs/core";
import roomsUnordered from "./rooms.json";
import { biomes2color, category2color } from "./biomes";
import uniqBy from "lodash.uniqby";

export const rooms = uniqBy(roomsUnordered, room =>
  room.name.toLowerCase()
).sort((roomA, roomB) => {
  const categorySort = roomA.category.localeCompare(roomB.category);
  if (categorySort === 0) {
    return roomA.name.localeCompare(roomB.name);
  } else {
    return categorySort;
  }
});

// console.log(
//   Object.keys(
//     rooms.reduce((set, char) => {
//       set[char.category] = char;
//       return set;
//     }, {})
//   )
// );

// export const rooms = [
//   { name: "Dungeon", suggested: true },
//   { name: "Garden", suggested: false }
// ];

// export const rooms = Object.keys(category2color || {}).map(category => {
//   return {
//     name: category
//   };
// });

const filterRoom = (query, room, _index, exactMatch) => {
  const normalizedTitle = room.name.toLowerCase();
  const normalizedCategory = room.category.toLowerCase();
  const normalizedQuery = query.toLowerCase();

  if (exactMatch !== undefined) {
    console.log(exactMatch);
  }
  if (exactMatch) {
    return normalizedTitle === normalizedQuery;
  } else {
    return (
      `${normalizedTitle} ${normalizedCategory}`.indexOf(normalizedQuery) >= 0
    );
  }
};

const renderRoom = (room, { handleClick, modifiers, query }) => {
  if (!modifiers.matchesPredicate) {
    return null;
  }
  const text = `${room.name}`;
  return (
    <MenuItem
      active={modifiers.active}
      disabled={modifiers.disabled}
      label={(room.suggested ? "(Recommended ⭐️) " : "") + room.category}
      key={"" + room.id + room.suggested}
      onClick={handleClick}
      text={highlightText(text, query)}
    />
  );
};

function escapeRegExpChars(text) {
  return text.replace(/([.*+?^=!:${}()|\[\]\/\\])/g, "\\$1");
}

function highlightText(text, query) {
  let lastIndex = 0;
  const words = query
    .split(/\s+/)
    .filter(word => word.length > 0)
    .map(escapeRegExpChars);
  if (words.length === 0) {
    return [text];
  }
  const regexp = new RegExp(words.join("|"), "gi");
  const tokens = [];
  while (true) {
    const match = regexp.exec(text);
    if (!match) {
      break;
    }
    const length = match[0].length;
    const before = text.slice(lastIndex, regexp.lastIndex - length);
    if (before.length > 0) {
      tokens.push(before);
    }
    lastIndex = regexp.lastIndex;
    tokens.push(<strong key={lastIndex}>{match[0]}</strong>);
  }
  const rest = text.slice(lastIndex);
  if (rest.length > 0) {
    tokens.push(rest);
  }
  return tokens;
}

export function areRoomsEqual(roomA, roomB) {
  // Compare only the titles (ignoring case) just for simplicity.
  return roomA.name.toLowerCase() === roomB.name.toLowerCase();
}

function RoomSuggest({ disabled, selected, onSelect, suggestions = [] }) {
  const items = React.useMemo(
    () => [
      ...rooms
        .filter(room => suggestions.indexOf(room.id) >= 0)
        .map(room => ({ ...room, suggested: true })),
      ...rooms.filter(room => suggestions.indexOf(room.id) < 0)
      // ...rooms
    ],
    [suggestions]
  );
  return (
    <Suggest
      itemPredicate={filterRoom}
      itemRenderer={renderRoom}
      items={items}
      disabled={disabled}
      resetOnSelect={true}
      // createNewItemFromQuery={maybeCreateNewItemFromQuery}
      // createNewItemRenderer={maybeCreateNewItemRenderer}
      inputValueRenderer={room => room.name}
      itemsEqual={areRoomsEqual}
      selectedItem={items.find(r => selected && r.id === selected.id) || null}
      // we may customize the default filmSelectProps.items by
      // adding newly created items to the list, so pass our own.
      noResults={<MenuItem disabled={true} text="No results." />}
      onItemSelect={room => onSelect(room)}
      popoverProps={{ minimal: true }}
    />
  );
}
export default RoomSuggest;
