
/*****
 * Copyright (c) Meta Platforms, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react";
import ReactDOM from "react-dom";
import cx from "classnames";

import "./styles.css";
import RoomSuggest, { rooms } from "./RoomSuggest";
import CharactersSuggest from "./CharactersSuggest";
import ObjectsSuggest from "./ObjectsSuggest";
import Instructions from "./Instructions";
import SubmitForm from "./SubmitForm";
import {
  Button,
  ButtonGroup,
  Card,
  Intent,
  EditableText,
  H2,
  Dialog,
  Classes
} from "@blueprintjs/core";
import { lookupCategoryColor } from "./biomes";
import { useMLSuggestions, submit } from "./api";

// function getContrast50(hexcolor = "#") {
//   return parseInt(hexcolor.replace(/^#/, ""), 16) > 0xffffff / 2
//     ? "black"
//     : "white";
// }

function pickRandom(arr) {
  return arr[Math.floor(Math.random() * arr.length)];
}

function getContrastYIQ(hexcolor = "#") {
  hexcolor = hexcolor.replace(/^#/, "");
  var r = parseInt(hexcolor.substr(0, 2), 16);
  var g = parseInt(hexcolor.substr(2, 2), 16);
  var b = parseInt(hexcolor.substr(4, 2), 16);
  var yiq = (r * 299 + g * 587 + b * 114) / 1000;
  return yiq >= 128 ? "black" : "white";
}

const RANDOM_SEED = Math.ceil(Math.random() * 100000) + 100000;
const USE_ML = RANDOM_SEED % 2 === 0; /* use ML for even values */
// const USE_ML = true;

function Map({
  tiles,
  onSelect,
  selectedTile = [null, null],
  connections,
  onConnection
}) {
  const isConnected = (row, col, orientation) => {
    const matches = connections.filter(
      ([r, c, o]) => r === row && c === col && o === orientation
    );
    return matches.length > 0;
  };
  selectedTile = selectedTile === null ? [null, null] : selectedTile;

  const [emojiOffset, setEmojiOffset] = React.useState(0);
  React.useEffect(() => {
    const interval = setInterval(() => setEmojiOffset(e => e + 1), 1000);
    return () => clearInterval(interval);
  }, [emojiOffset, setEmojiOffset]);

  return (
    <div className="map">
      {tiles.map((row, rowIdx) => (
        <React.Fragment key={rowIdx}>
          <div className="row">
            {row.map((tile, colIdx) => (
              <React.Fragment key={colIdx}>
                <div
                  style={{
                    backgroundColor: lookupCategoryColor(
                      tile.location && tile.location.category
                    ),
                    color: getContrastYIQ(
                      lookupCategoryColor(
                        tile.location && tile.location.category
                      ) || "#eeeeee"
                    )
                  }}
                  className={cx("tile", {
                    selected:
                      selectedTile[0] === rowIdx && selectedTile[1] === colIdx
                  })}
                  onClick={() => onSelect(rowIdx, colIdx)}
                >
                  {tile.location && tile.location.name}
                  <div className="char-emojis">
                    {(tile.chars || []).map(
                      char => char.emojis[emojiOffset % char.emojis.length]
                    )}
                  </div>
                  <div className="obj-emojis">
                    {(tile.objs || []).map(
                      obj => obj.emojis[emojiOffset % obj.emojis.length]
                    )}
                  </div>
                </div>
                {colIdx < 2 ? (
                  <div
                    className={cx("connector", {
                      connected: isConnected(rowIdx, colIdx, "v")
                    })}
                    onClick={() => onConnection(rowIdx, colIdx, "v")}
                  />
                ) : null}
              </React.Fragment>
            ))}
          </div>
          {rowIdx < 2 ? (
            <div className="row spacer">
              {row.map((tile, colIdx) => (
                <React.Fragment key={colIdx}>
                  <div
                    className={cx("horizontal", "connector", {
                      connected: isConnected(rowIdx, colIdx, "h")
                    })}
                    onClick={() => onConnection(rowIdx, colIdx, "h")}
                  />
                </React.Fragment>
              ))}
            </div>
          ) : null}
        </React.Fragment>
      ))}
    </div>
  );
}

const RANDOM_ROOM = pickRandom(rooms);

function App() {

  const gameMap = [
    [{ location: null }, { location: null }, { location: null }],
    [{ location: null }, { location: RANDOM_ROOM }, { location: null }],
    [{ location: null }, { location: null }, { location: null }]
  ];

  const [title, setTitle] = React.useState("");
  const [tiles, setTiles] = React.useState(gameMap);
  const [selectedTile, setSelectedTile] = React.useState(null);
  const [connections, setConnections] = React.useState([]);
  const [location, setLocation] = React.useState(null);
  const [characters, setCharacters] = React.useState([]);
  const [objects, setObjects] = React.useState([]);

  const [isDone, setIsDone] = React.useState(false);

  const [firstClickTime, setFirstClickTime] = React.useState(null);

  const selectedIndex = selectedTile
    ? selectedTile[0] * 3 + selectedTile[1] + 1
    : null;

  const suggestions = useMLSuggestions(
    tiles,
    connections,
    /*enabled: */ USE_ML,
    { selectedTile, location, characters, objects }
  );

  return (
    <div>
      {/* {isDone && ( */}
      <Dialog
        icon="thumbs-up"
        // onClose={this.handleClose}
        title="Completed"
        isOpen={isDone}
        isCloseButtonShown={false}
      >
        <div className={Classes.DIALOG_BODY}>
          You have completed the task! Thank you!
        </div>
      </Dialog>
      {/* )} */}
      <Instructions />
      {/* <div>{selectedTile}</div> */}
      {/* <div>{connections}</div> */}
      <hr />
      <H2 style={{ marginLeft: 30 }}>
        <EditableText
          intent={Intent.NONE}
          value={title}
          onChange={newTitle => setTitle(newTitle)}
          maxLength={200}
          placeholder="Click here to give this world a name..."
          selectAllOnFocus={true}
        />
      </H2>

      <Map
        tiles={tiles}
        connections={connections}
        onConnection={(row, col, orientation) => {
          const filtered = connections.filter(
            ([r, c, o]) => r !== row || c !== col || o !== orientation
          );
          if (filtered.length !== connections.length) {
            setConnections(filtered);
          } else {
            setConnections([...connections, [row, col, orientation]]);
          }
        }}
        selectedTile={selectedTile}
        onSelect={(row, col) => {
          if (firstClickTime === null) {
            setFirstClickTime(new Date());
          }

          // console.log("here");)
          if (
            selectedTile !== null &&
            selectedTile[0] === row &&
            selectedTile[1] === col
          ) {
            setSelectedTile(null);
            setLocation(null);
            return;
          }

          setSelectedTile([row, col]);
          setLocation(tiles[row][col].location);
          setCharacters(tiles[row][col].chars || []);
          setObjects(tiles[row][col].objs || []);
        }}
      />
      <form
        onSubmit={e => {
          e.preventDefault();
        }}
      >
        {/* <input
          disabled={selectedTile === null}
          value={text}
          onChange={e => setText(e.target.value)}
        />
        <button disabled={selectedTile === null}>Update</button> */}
        <div>
          <Card>
            <h3 className="bp3-heading">
              {selectedTile === null ? (
                <div>
                  Directions:
                  <ul>
                    <li>Select a map tile above to update it.</li>
                    <li>
                      By default, all map tiles are connected. Click in-between
                      tiles to create a boundary and cut off connections, where
                      you think it doesn't make sense to connect tiles.
                    </li>
                  </ul>
                </div>
              ) : (
                "Modify this map tile:"
              )}
            </h3>
            {/* <p className="bp3-text">Select a tile above to pick a room</p> */}
            {selectedTile === null || (
              <div>
                <label className="bp3-label bp3-inline">
                  Location:
                  <RoomSuggest
                    suggestions={
                      suggestions &&
                      suggestions[selectedIndex] &&
                      suggestions[selectedIndex].rooms
                    }
                    // suggestions={[262]}
                    disabled={selectedTile === null}
                    selected={location}
                    onSelect={room => {
                      setLocation(room);
                    }}
                  />
                </label>
                <div>
                  <label
                    className="bp3-label bp3-inline"
                    style={{ display: "inline-block", marginRight: 10 }}
                  >
                    Add characters:
                  </label>
                  <CharactersSuggest
                    suggestions={
                      suggestions &&
                      suggestions[selectedIndex] &&
                      suggestions[selectedIndex].characters
                    }
                    // suggestions={[1262]}
                    disabled={selectedTile === null}
                    selected={characters}
                    onSelect={chars => {
                      setCharacters([...characters, chars]);
                    }}
                    onDeselect={(tag, idx) => {
                      setCharacters(
                        characters.filter((char, i) => tag !== char.name)
                      );
                    }}
                  />
                </div>
                <div>
                  <label
                    className="bp3-label bp3-inline"
                    style={{ marginRight: 10 }}
                  >
                    Add objects:
                  </label>
                  <ObjectsSuggest
                    suggestions={
                      suggestions &&
                      suggestions[selectedIndex] &&
                      suggestions[selectedIndex].objects
                    }
                    // suggestions={[2425]}
                    disabled={selectedTile === null}
                    selected={objects}
                    onSelect={obj => {
                      setObjects([...objects, obj]);
                    }}
                    onDeselect={(tag, idx) => {
                      setObjects(objects.filter((obj, i) => tag !== obj.name));
                    }}
                  />
                </div>
                <ButtonGroup style={{ marginTop: 10 }}>
                  <Button
                    intent={Intent.SUCCESS}
                    disabled={selectedTile === null}
                    onClick={() => {
                      setTiles(
                        tiles.map((row, rowIdx) =>
                          row.map((tile, colIdx) => {
                            if (
                              rowIdx === selectedTile[0] &&
                              colIdx === selectedTile[1]
                            ) {
                              return {
                                location: location,
                                chars: characters,
                                objs: objects
                              };
                            } else {
                              return tile;
                            }
                          })
                        )
                      );
                      setSelectedTile(null);
                      setLocation(null);
                      setCharacters([]);
                      setObjects([]);
                    }}
                    text="Update"
                    // type="submit"
                  />
                  <Button
                    disabled={selectedTile === null}
                    text="Reset"
                    onClick={() => {
                      setLocation(null);
                      setCharacters([]);
                      setObjects([]);
                    }}
                  />
                </ButtonGroup>
              </div>
            )}
          </Card>
        </div>
        <SubmitForm
          uniqueId={RANDOM_SEED}
          useModel={USE_ML}
          onSubmit={() => {
            submit(
              tiles,
              connections,
              title,
              firstClickTime ? (new Date() - firstClickTime) / 1000 : 0
            );
            setIsDone(true);
          }}
        />
      </form>
    </div>
  );
}

const rootElement = document.getElementById("root");
ReactDOM.render(<App />, rootElement);
