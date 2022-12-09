/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react";
import { Link } from "react-router-dom";
import { Intent, Spinner, RadioGroup, Radio } from "@blueprintjs/core";
import AnimateHeight from "react-animate-height";
import { startCase } from "lodash";
import ReactPaginate from "react-paginate";

import CONFIG from "../config";
import { useAPI } from "../utils";

function ExplorePage() {
  const [selectedEntity, setSelectedEntity] = React.useState("object");
  const [page, setPage] = React.useState(0);

  const [searchText, setSearchText] = React.useState("");
  const { loading, result } = useAPI(
    CONFIG,
    "/entities/" + selectedEntity + "?search=" + searchText + "&page=" + page
  );

  return (
    <div>
      <h2 data-testid="header" className="bp3-heading">
        Explore
      </h2>
      <div className="bp3-text-large">
        Search across the LIGHT database for existing objects, characters, or
        rooms.
      </div>
      <div
        className="bp3-input-group bp3-large"
        style={{ margin: "20px 0px 10px" }}
      >
        <span className="bp3-icon bp3-icon-search" />
        <input
          className="bp3-input"
          type="search"
          placeholder="Search..."
          dir="auto"
          value={searchText}
          onChange={(e) => {
            setSearchText(e.target.value);
            setPage(0);
          }}
        />
      </div>
      <div style={{ display: "flex", marginBottom: 30 }}>
        <span style={{ margin: "0px 20px 0px 40px" }}>Searching category:</span>
        <RadioGroup
          inline
          large
          onChange={(e) => {
            setSelectedEntity(e.target.value);
            setPage(0);
          }}
          selectedValue={selectedEntity}
        >
          <Radio data-testid="radio-object" label="Objects" value="object" />
          <Radio
            data-testid="radio-character"
            label="Characters"
            value="character"
          />
          <Radio data-testid="radio-room" label="Rooms" value="room" />
        </RadioGroup>
      </div>

      {loading ? (
        <Spinner intent={Intent.PRIMARY} />
      ) : (
        <>
          <ItemsList
            items={result.data}
            descriptionField={
              selectedEntity === "room" ? "description" : "physical_description"
            }
            additionalFields={
              selectedEntity === "room"
                ? [{ name: "Backstory", key: "backstory" }]
                : []
            }
            selectedEntity={selectedEntity}
          />
          <div style={{ margin: "20px" }}>
            <ReactPaginate
              previousLabel={"previous"}
              nextLabel={"next"}
              breakLabel={"..."}
              forcePage={page}
              pageCount={result.total_pages}
              marginPagesDisplayed={2}
              pageRangeDisplayed={5}
              onPageChange={(data) => setPage(data.selected)}
              containerClassName={"pagination"}
              subContainerClassName={"pages pagination"}
              activeClassName={"active"}
            />
          </div>
        </>
      )}
    </div>
  );
}

function ItemsList({
  items,
  descriptionField,
  additionalFields = [],
  selectedEntity,
}) {
  const [state, setState] = React.useState({
    expanded: -1,
    animating: 0,
    nextState: -1,
  });

  function handleTrClick(index) {
    if (state.expanded === -1) {
      setState({ expanded: index, animating: 2, nextState: -1 });
    } else if (state.expanded === index) {
      setState({ expanded: index, animating: 3, nextState: -1 });
    } else {
      setState({ ...state, animating: 3, nextState: index });
    }
  }

  if (items === undefined || items.length === 0) {
    return <span>No items found.</span>;
  } else {
    return (
      <table
        data-testid="table-explore"
        style={{ width: "100%" }}
        className="bp3-html-table bp3-html-table-condensed bp3-interactive"
      >
        <thead>
          <tr>
            <th>Name</th>
            <th>Description</th>
            {additionalFields.map((field) => (
              <th key={field}>{field.name}</th>
            ))}

            <th>ID</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item, index) => (
            <React.Fragment key={item.id}>
              <tr
                onClick={() => handleTrClick(index)}
                data-testid="tr-explore"
                style={{
                  background:
                    index % 2 === 0 ? "rgba(191, 204, 214, 0.15)" : undefined,
                }}
              >
                <td>
                  <strong>{item.name}</strong>
                </td>
                <td>{item[descriptionField]}</td>
                {additionalFields.map((field) => (
                  <td key={field.name}>{item[field.key]}</td>
                ))}
                <td>{item.id}</td>
              </tr>
              <tr
                style={{
                  background:
                    index % 2 === 0 ? "rgba(191, 204, 214, 0.15)" : undefined,
                }}
              >
                <td
                  colSpan={5}
                  style={{
                    display: state.expanded === index ? undefined : "none",
                    padding: 0,
                    cursor: "unset",
                  }}
                >
                  <AnimateHeight
                    duration={500}
                    height={
                      state.expanded === index &&
                      (state.animating === 2 || state.animating === 0)
                        ? "auto"
                        : 0
                    }
                    easing={"ease"}
                    onAnimationEnd={() =>
                      setState({
                        nextState: -1,
                        expanded:
                          state.animating === 2 ? index : state.nextState,
                        animating:
                          state.animating === 3 && state.nextState !== -1
                            ? 2
                            : 0,
                      })
                    }
                    animateOpacity={true}
                  >
                    {state.expanded === index && (
                      <ExpandedTab
                        item={item}
                        selectedEntity={selectedEntity}
                      />
                    )}
                  </AnimateHeight>
                </td>
              </tr>
            </React.Fragment>
          ))}
        </tbody>
      </table>
    );
  }
}

function ExpandedTab({ item, selectedEntity }) {
  return (
    <>
      <div
        data-testid="dropdown"
        style={{
          padding: "20px 40px 0 40px",
        }}
      >
        <div
          style={{
            display: "flex",
            flexDirection: "column",
          }}
        >
          {Object.keys(item).map((key, index) => (
            <p key={index}>
              <strong>{startCase(key)}</strong>: {item[key]}
            </p>
          ))}
        </div>
      </div>
      <div
        style={{
          display: "flex",
          padding: "0 20px 20px 20px",
          justifyContent: "flex-end",
        }}
      >
        <Link
          style={{ margin: "0 5px" }}
          className="bp3-button bp3-small"
          to={{
            pathname: `/create`,
            state: {
              type: selectedEntity,
              entity: item,
            },
          }}
        >
          Create From
        </Link>
        <Link
          style={{ margin: "0 5px" }}
          className="bp3-button bp3-small"
          to={{
            pathname: `/edit/${item.id}`,
            state: {
              type: selectedEntity,
              entity: item,
            },
          }}
        >
          Edit
        </Link>
      </div>
    </>
  );
}

export default ExplorePage;
