import classNames from "classnames";
import React from "react";
import {
  NumericInput,
  Classes,
  ControlGroup,
  FormGroup,
  Overlay,
  Tooltip,
  Position,
  Icon,
  Switch,
  Button
} from "@blueprintjs/core";

import {
  ListWorlds,
  useWorldBuilder,
  MAX_HEIGHT,
  MAX_WIDTH,
  MAX_FLOORS
} from "./worldbuilding/utils";
import Grid from "./worldbuilding/Grid";
import FloorSelector from "./worldbuilding/FloorSelector";

function WorldBuilderPage({ location }) {
  return (
    <div>
      <h2 data-testid="header" className="bp3-heading">
        World Builder
      </h2>
      <div>
        <WorldBuilder upload={location.state} />
      </div>
    </div>
  );
}

// TODO:  Add save, load, delete, list buttons
function WorldBuilder({ upload }) {
  const state = useWorldBuilder(upload);
  const [advanced, setAdvanced] = React.useState(false);
  const [isOverlayOpen, toggleOverlay] = React.useState(false);
  const classes = classNames(
    Classes.CARD,
    Classes.ELEVATION_4,
  );
  return (
    <>
    <Overlay onOpening={() => ListWorlds()} isOpen={isOverlayOpen} onClose={() => toggleOverlay(!isOverlayOpen)} hasBackdrop={true} autoFocus={true} usePortal={true}>
      <div className={classes}>
          <p>
              This is a simple container with some inline styles to position it on the screen. Its CSS
              transitions are customized for this example only to demonstrate how easily custom
              transitions can be implemented.
          </p>
          <p>
              Click the "Focus button" below to transfer focus to the "Show overlay" trigger button
              outside of this overlay. If persistent focus is enabled, focus will be constrained to the
              overlay. Use the <b>tab</b> key to move to the next focusable element to illustrate
              this effect.
          </p>
          <p>
              Click the "Make me scroll" button below to make this overlay's content really tall, which
              will make the overlay's container (but not the page) scrollable
          </p>
          <Button onClick={() => toggleOverlay(!isOverlayOpen)} style={{ margin: "" }}>
              Close
          </Button>
        </div>
      </Overlay>
      <FormGroup
        inline
        label="World Dimensions"
        labelInfo={`WxH (Max ${MAX_WIDTH}x${MAX_HEIGHT})`}
      >
        <ControlGroup>
          <NumericInput
            value={state.dimensions.width}
            style={{ width: "3rem" }}
            max={MAX_WIDTH}
            min={1}
            onValueChange={value => {
              state.setDimensions({ ...state.dimensions, width: value });
            }}
          />

          <NumericInput
            value={state.dimensions.height}
            style={{ width: "3rem" }}
            max={MAX_HEIGHT}
            min={1}
            onValueChange={value => {
              state.setDimensions({ ...state.dimensions, height: value });
            }}
          />
        </ControlGroup>
      </FormGroup>
      <FormGroup
        inline
        label={
          <>
            Floor{" "}
            <Tooltip
              content={
                "Right click floor for more options. Click and hold floor to reorder."
              }
              position={Position.BOTTOM}
              className="inline"
            >
              <Icon icon="help" />
            </Tooltip>
          </>
        }
        labelInfo={`Max ${MAX_FLOORS}`}
        style={{ marginBottom: "0px" }}
      >
        <FloorSelector
          max={MAX_FLOORS}
          manager={state.floorManager}
          map={state.map}
          currFloor={state.currFloor}
        />
      </FormGroup>
      <FormGroup inline label="Advanced">
        <Switch onChange={() => setAdvanced(!advanced)} checked={!!advanced} />
      </FormGroup>
      <Grid state={state} initialShowAdvanced={advanced} />
      <div
        style={{
          display: "flex",
          justifyContent: "flex-end",
          position: "fixed",
          bottom: 0,
          left: 0,
          right: 0,
          height: "50px"
        }}
        className="bp3-navbar"
      >
        <Button
          onClick={() => toggleOverlay(!isOverlayOpen)} 
          intent="primary"
          style={{ margin: "10px" }}
        >
          Manage Worlds
        </Button>
        <Button
          onClick={state.postWorld}
          intent="primary"
          style={{ margin: "10px" }}
        >
          Save
        </Button>
        <Button
          onClick={state.exportWorld}
          intent="primary"
          style={{ margin: "10px" }}
        >
          Export
        </Button>
        <Button
          onClick={state.postEdges}
          intent="primary"
          style={{ margin: "10px" }}
        >
          Commit Edges
        </Button>
      </div>
    </>
  );
}

export default WorldBuilderPage;
