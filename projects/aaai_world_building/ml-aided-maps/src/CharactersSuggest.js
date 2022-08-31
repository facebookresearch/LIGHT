
/*****
 * Copyright (c) Meta Platforms, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react";
import { MultiSelect } from "@blueprintjs/select";
import { MenuItem } from "@blueprintjs/core";
import charsUnordered from "./characters.json";
import { biomes2color, category2color } from "./biomes";
import uniqBy from "lodash.uniqby";

const characters = uniqBy(charsUnordered, char => char.name.toLowerCase()).sort(
  (charA, charB) => {
    const categorySort = charA.char_type.localeCompare(charB.char_type);
    if (categorySort === 0) {
      return charA.name.localeCompare(charB.name);
    } else {
      return categorySort;
    }
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

const filterCharacters = (query, character, _index, exactMatch) => {
  const normalizedTitle = character.name.toLowerCase();
  const normalizedQuery = query.toLowerCase();

  if (exactMatch !== undefined) {
    console.log(exactMatch);
  }
  if (exactMatch) {
    return normalizedTitle === normalizedQuery;
  } else {
    return (
      `${normalizedTitle} ${character.char_type}`.indexOf(normalizedQuery) >= 0
    );
  }
};

const renderCharacter = (character, { handleClick, modifiers, query }) => {
  if (!modifiers.matchesPredicate) {
    return null;
  }
  const text = `${character.name}`;
  return (
    <MenuItem
      active={modifiers.active}
      disabled={modifiers.disabled}
      label={
        (character.suggested ? "(Recommended ⭐️) " : "") +
        character.emojis.join(" ") +
        " " +
        character.char_type
      }
      key={character.id}
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

export function areCharsEqual(charA, charB) {
  // Compare only the titles (ignoring case) just for simplicity.
  return charA.name === charB.name;
}

function CharactersSuggest({
  className,
  disabled,
  selected = [],
  onSelect,
  onDeselect,
  suggestions = []
}) {
  const items = React.useMemo(
    () => [
      ...characters
        .filter(char => suggestions.indexOf(char.id) >= 0)
        .map(char => ({ ...char, suggested: true })),
      ...characters.filter(char => suggestions.indexOf(char.id) < 0)
    ],
    [suggestions]
  );

  const selectedNames = selected.map(s => s.name);
  return (
    <MultiSelect
      className={className}
      itemPredicate={filterCharacters}
      itemRenderer={renderCharacter}
      items={items}
      disabled={disabled}
      resetOnSelect={true}
      // createNewItemFromQuery={maybeCreateNewItemFromQuery}
      // createNewItemRenderer={maybeCreateNewItemRenderer}
      // inputValueRenderer={room => room.name}
      itemsEqual={areCharsEqual}
      selectedItems={items.filter(r => selectedNames.indexOf(r.name) >= 0)}
      tagRenderer={char => char.name}
      // we may customize the default filmSelectProps.items by
      // adding newly created items to the list, so pass our own.
      tagInputProps={{
        onRemove: (tag, idx) => {
          onDeselect(tag, idx);
        }
      }}
      noResults={<MenuItem disabled={true} text="No results." />}
      onItemSelect={char => onSelect(char)}
      popoverProps={{ minimal: true }}
    />
  );
}
export default CharactersSuggest;
