/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react";
import { MultiSelect } from "@blueprintjs/select";
import { MenuItem } from "@blueprintjs/core";
import objsUnordered from "./objects.json";
import { biomes2color, category2color } from "./biomes";
import uniqBy from "lodash.uniqby";

const objects = uniqBy(objsUnordered, obj => obj.name.toLowerCase()).sort(
  (objA, objB) => {
    // const categorySort = objA.obj_type.localeCompare(objB.obj_type);
    // if (categorySort === 0) {
    return objA.name.localeCompare(objB.name);
    // } else {
    //   return categorySort;
    // }
  }
);

// export const rooms = [
//   { name: "Dungeon", suggested: true },
//   { name: "Garden", suggested: false }
// ];

// export const rooms = Object.keys(category2color || {}).map(category => {
//   return {
//     name: category
//   };
// });

const filterObjects = (query, object, _index, exactMatch) => {
  const normalizedTitle = object.name.toLowerCase();
  const normalizedQuery = query.toLowerCase();

  if (exactMatch !== undefined) {
    console.log(exactMatch);
  }
  if (exactMatch) {
    return normalizedTitle === normalizedQuery;
  } else {
    return `${normalizedTitle}`.indexOf(normalizedQuery) >= 0;
  }
};

const renderObject = (object, { handleClick, modifiers, query }) => {
  if (!modifiers.matchesPredicate) {
    return null;
  }
  const text = `${object.name}`;
  return (
    <MenuItem
      active={modifiers.active}
      disabled={modifiers.disabled}
      label={
        (object.suggested ? "(Recommended ⭐️) " : "") + object.emojis.join(" ")
      }
      key={object.id}
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

export function areCharsEqual(objA, objB) {
  // Compare only the titles (ignoring case) just for simplicity.
  return objA.name === objB.name;
}

function ObjectsSuggest({
  className,
  disabled,
  selected = [],
  onSelect,
  onDeselect,
  suggestions = []
}) {
  const items = React.useMemo(
    () => [
      ...objects
        .filter(obj => suggestions.indexOf(obj.id) >= 0)
        .map(obj => ({ ...obj, suggested: true })),
      ...objects.filter(obj => suggestions.indexOf(obj.id) < 0)
    ],
    [suggestions]
  );
  const selectedNames = selected.map(s => s.name);
  return (
    <MultiSelect
      className={className}
      itemPredicate={filterObjects}
      itemRenderer={renderObject}
      items={items}
      disabled={disabled}
      resetOnSelect={true}
      // createNewItemFromQuery={maybeCreateNewItemFromQuery}
      // createNewItemRenderer={maybeCreateNewItemRenderer}
      // inputValueRenderer={room => room.name}
      itemsEqual={areCharsEqual}
      selectedItems={items.filter(r => selectedNames.indexOf(r.name) >= 0)}
      tagRenderer={obj => obj.name}
      // we may customize the default filmSelectProps.items by
      // adding newly created items to the list, so pass our own.
      tagInputProps={{
        onRemove: (tag, idx) => {
          onDeselect(tag, idx);
        }
      }}
      noResults={<MenuItem disabled={true} text="No results." />}
      onItemSelect={obj => onSelect(obj)}
      popoverProps={{ minimal: true }}
    />
  );
}
export default ObjectsSuggest;
