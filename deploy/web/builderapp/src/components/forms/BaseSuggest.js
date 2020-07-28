import React from "react";
import { Intent, Menu, MenuItem } from "@blueprintjs/core";
import { Suggest } from "@blueprintjs/select";
import equal from "fast-deep-equal";
import "@blueprintjs/select/lib/css/blueprint-select.css";

import CONFIG from "../../config";
import { useAPI } from "../../utils";

const SUGGEST_SIZE = 100;

function BaseSuggest({
  id,
  name,
  errors,
  touched,
  setFieldTouched,
  formValue,
  handleChange,
  type,
  onItemSelect,
  entities,
}) {
  const [items, setItems] = React.useState([]);
  const [query, setQuery] = React.useState("");
  const [currItem, setCurrItem] = React.useState(formValue);
  const { loading, result } = useAPI(
    CONFIG,
    `/entities/${type}?search=${query}`
  );

  React.useEffect(() => {
    if (!loading) {
      if (entities) {
        const localEntities = Object.values(entities[type]);
        const results = localEntities
          .concat(result.slice(0, SUGGEST_SIZE + localEntities.length + 1))
          .filter(
            (item, index, self) =>
              self.findIndex((t) => equal(t, item)) === index
          );

        return setItems(results);
      }
      return setItems(result);
    }
  }, [result, loading, entities, type]);

  React.useEffect(() => {
    if (entities) {
      return setCurrItem(formValue);
    }
    // When Reset is clicked on the form
    if (isNaN(formValue)) {
      return setCurrItem(null);
    }
    for (let item in items) {
      if (items[item].id === formValue) {
        return setCurrItem(items[item]);
      }
    }
  }, [formValue, items, entities]);

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

  return (
    <div onBlur={(e) => setFieldTouched(name)}>
      <Suggest
        id={id}
        name={name}
        items={items}
        itemRenderer={renderOption}
        itemListRenderer={renderItemList}
        inputValueRenderer={(item) =>
          entities && entities[type][item]
            ? entities[type][item].name
            : item.name
        }
        inputProps={{
          intent: errors && touched ? Intent.DANGER : null,
          "data-testid": "base-suggest",
        }}
        onItemSelect={(e) => {
          if (onItemSelect) {
            const result = onItemSelect(e, type);
            setCurrItem(result);
            handleChange(name, result, e);
          } else {
            setCurrItem(e);
            handleChange(name, e.id, e);
          }
          setQuery("");
        }}
        popoverProps={{ usePortal: false }}
        itemPredicate={filterItems}
        selectedItem={currItem}
        query={query}
        onQueryChange={(q) => setQuery(q)}
        resetOnQuery={true}
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

function renderOption(obj, { handleClick, modifiers, index }) {
  if (!modifiers.matchesPredicate) {
    return null;
  }

  return (
    <MenuItem
      active={modifiers.active}
      key={index}
      onClick={handleClick}
      text={obj.name}
      shouldDismissPopover={false}
    />
  );
}

export default BaseSuggest;
