
/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react";
import { Intent, Menu, MenuItem, Tooltip, Position } from "@blueprintjs/core";
import { MultiSelect } from "@blueprintjs/select";
import equal from "fast-deep-equal";
import "@blueprintjs/select/lib/css/blueprint-select.css";

import CONFIG from "../../config";
import { useAPI, get_source } from "../../utils";

const SUGGEST_SIZE = 100;

function BaseMultiSelect({
  id,
  name,
  errors,
  touched,
  setFieldTouched,
  formValue,
  handleChange,
  type,
  tooltip,
  onItemSelect,
  entities,
  suggestionSource,
}) {
  const [items, setItems] = React.useState([]);
  const [query, setQuery] = React.useState("");
  const [currItems, setCurrItems] = React.useState([]);
  const { loading: loadingModel, result: modelResult } = useAPI(
    CONFIG,
    `/suggestions/${type}/${get_source(suggestionSource, entities)}`
  );
  const { loading, result } = useAPI(
    CONFIG,
    `/entities/${type}?search=${query}`
  );

  let options = result;

  if (!loading && !loadingModel && modelResult !== undefined && !query) {
    options = modelResult.concat(result);
  }

  React.useEffect(() => {
    if (!loading) {
      if (entities) {
        const localEntities = Object.values(entities[type]);
        const results = localEntities
          .concat(options.slice(0, SUGGEST_SIZE + localEntities.length + 1))
          .filter(
            (item, index, self) =>
              self.findIndex((t) => equal(t, item)) === index
          );

        return setItems(results);
      }
      return setItems(options);
    }
  }, [result, modelResult, loading, entities, type]);

  React.useEffect(() => {
    // When Reset is clicked on the form
    setCurrItems(formValue);
  }, [formValue, items]);

  const filterItems = (query, obj, _index, exactMatch) => {
    const normalizedTitle = obj.name.toLowerCase();
    const normalizedQuery = query.toLowerCase();
    if (exactMatch) {
      return normalizedTitle === normalizedQuery;
    } else {
      let string = "";
      for (let key in obj) {
        string += obj[key] + ". ";
      }
      const result = string.toLowerCase().indexOf(normalizedQuery) >= 0;
      return result;
    }
  };

  const removeTag = (_value, index) => {
    const newItems = currItems.filter((_item, i) => {
      return i !== index;
    });
    const change = formValue.filter((_item, i) => {
      return i !== index;
    });
    setCurrItems(newItems);
    handleChange(name, change);
  };

  const renderOption = (obj, { handleClick, modifiers, index }) => {
    if (!modifiers.matchesPredicate) {
      return null;
    }

    return (
      <MenuItem
        active={modifiers.active}
        key={index}
        onClick={handleClick}
        text={
          tooltip ? (
            <Tooltip
              content={obj[tooltip]}
              targetTagName="div"
              popoverClassName="popover-tooltip"
              position={Position.TOP_RIGHT}
              usePortal={true}
            >
              {obj.name}
            </Tooltip>
          ) : (
            obj.name
          )
        }
        shouldDismissPopover={false}
      />
    );
  };

  return (
    <div onBlur={(e) => setFieldTouched(name)}>
      <MultiSelect
        id={id}
        name={name}
        items={items}
        itemRenderer={renderOption}
        itemListRenderer={renderItemList}
        tagInputProps={{
          intent: errors && touched ? Intent.DANGER : null,
          "data-testid": "base-multi-select",
          onRemove: removeTag,
        }}
        onItemSelect={(e) => {
          if (onItemSelect) {
            const result = onItemSelect(e, type);
            setCurrItems([...currItems, result]);
            handleChange(name, [...formValue, result], e);
          } else {
            setCurrItems([...currItems, e]);
            handleChange(name, [...formValue, e.id]);
          }
          setQuery("");
        }}
        popoverProps={{ usePortal: false }}
        itemPredicate={filterItems}
        selectedItems={currItems}
        query={query}
        onQueryChange={(q) => setQuery(q)}
        resetOnQuery={true}
        tagRenderer={(item) => {
          return entities && entities[type][item]
            ? entities[type][item].name
            : item.name;
        }}
      />
    </div>
  );
}

function renderItemList({ filteredItems, renderItem }) {
  const topResults = filteredItems.slice(0, SUGGEST_SIZE);
  return (
    <Menu>
      {filteredItems.length > 0 ? (
        <>
          {topResults.map((item, index) => {
            return renderItem(item, index);
          })}
          {filteredItems.length > SUGGEST_SIZE && (
            <MenuItem
              style={{ textAlign: "center" }}
              disabled={true}
              text="..."
            />
          )}
        </>
      ) : (
        <MenuItem disabled={true} text="No results." />
      )}
    </Menu>
  );
}

export default BaseMultiSelect;
