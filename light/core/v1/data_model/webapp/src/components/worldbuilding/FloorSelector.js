import React from "react";
import {
  ContextMenuTarget,
  Menu,
  MenuItem,
  Button,
  InputGroup,
  Alert,
  Intent
} from "@blueprintjs/core";
import Reorder from "react-reorder";
import createReactClass from "create-react-class";
import { isEmpty } from "lodash";

import { MAX_FLOORS } from "./utils";

/**
 * Component for interacting with floors of the map.
 * Uses react-reorder for the reorderable list.
 */
function FloorSelector({ manager, map, currFloor }) {
  // Prevents switching floors on a context click (which can cause several components to remount and break links)
  const [contextShowing, setContextShowing] = React.useState(false);
  const [editing, setEditing] = React.useState(null);
  // Contains all data for a confirm alert (on Delete, or Reorder actions)
  const [confirmAlert, setConfirmAlert] = React.useState({});
  const inputRef = React.createRef();

  const floors = map.map(({ name }, index) => {
    return { name, index };
  });

  // Template component for each Floor Button
  const FloorButton = ContextMenuTarget(
    createReactClass({
      keypressHandler: function(event) {
        if (event.key === "Enter") {
          inputRef.current.blur();
        }
      },
      renderContextMenu: function() {
        setContextShowing(true);
        return (
          <Menu>
            <MenuItem
              icon="edit"
              onClick={() => setEditing(this.props.item.index)}
              text="Edit Floor Name"
            />
            <MenuItem
              icon="delete"
              disabled={floors.length <= 1}
              onClick={() => {
                setConfirmAlert({
                  confirmButtonText: "Confirm Delete",
                  icon: "trash",
                  intent: Intent.DANGER,
                  onConfirm: () => {
                    manager.deleteFloor(this.props.item.index);
                    setConfirmAlert({});
                  },
                  content: `Are you sure you want to delete the entire ${this.props.item.name} floor? All data on this floor and connections to this floor will be reset.`
                });
              }}
              text="Delete Floor"
            />
          </Menu>
        );
      },
      onContextMenuClose: function() {
        setContextShowing(false);
      },
      handleBlur: function(e) {
        manager.editFloorName(e.target.value, this.props.item.index);
        setEditing(null);
      },
      componentDidMount: function() {
        if (editing === this.props.item.index) {
          inputRef.current.focus();
          inputRef.current.select();
        }
      },
      render: function() {
        return (
          <div
            style={{
              textAlign: "center",
              width: "100%",
              height: "100%",
              lineHeight: "30px",
              padding: "0px 5px"
            }}
          >
            {editing !== null && editing === this.props.item.index ? (
              <InputGroup
                inputRef={inputRef}
                onBlur={this.handleBlur}
                defaultValue={this.props.item.name}
                onKeyPress={event => this.keypressHandler(event)}
              />
            ) : (
              <div>{this.props.item.name}</div>
            )}
          </div>
        );
      }
    })
  );

  // Prevent floor selection if context or editing has been triggered (prevents unintended switching)
  const selectFloor = (_e, _floor, index) => {
    if (!contextShowing && !editing) {
      manager.setCurrFloor(index);
    }
  };

  const handleReorder = (_e, _floor, initialIndex, newIndex) => {
    if (initialIndex !== newIndex) {
      setConfirmAlert({
        confirmButtonText: "Confirm Reorder",
        icon: "layers",
        intent: Intent.WARNING,
        onConfirm: () => {
          manager.reorderFloors(initialIndex, newIndex);
          setConfirmAlert({});
        },
        content: `Are you sure you want to reorder the entire ${floors[newIndex].name} floor? All connections to and from this floor, in both positions, will be reset.`
      });
    }
  };

  return (
    <>
      <Alert
        confirmButtonText={confirmAlert.confirmButtonText}
        cancelButtonText="Cancel"
        icon={confirmAlert.icon}
        intent={confirmAlert.intent}
        isOpen={!isEmpty(confirmAlert)}
        onCancel={() => {
          if (confirmAlert.onCancel) {
            confirmAlert.onCancel();
          }
          setConfirmAlert({});
        }}
        onConfirm={confirmAlert.onConfirm}
      >
        <p>{confirmAlert.content}</p>
      </Alert>
      <div
        style={{
          display: "flex"
        }}
      >
        <Button
          disabled={map.length >= MAX_FLOORS}
          icon="add"
          onClick={manager.addFloor}
          style={{
            height: "30px"
          }}
        />
        <Reorder
          holdTime="200"
          callback={handleReorder}
          template={FloorButton}
          itemKey="index"
          list={floors}
          selected={floors[currFloor]}
          itemClicked={selectFloor}
          lock="vertical"
          itemClass="bp3-button floor-button"
        />
      </div>
    </>
  );
}

export default FloorSelector;
