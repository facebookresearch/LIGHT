import React from "react";
import {
  NumericInput,
  ControlGroup,
  FormGroup,
  Tooltip,
  Position,
  Icon,
  Switch,
  Button,
} from "@blueprintjs/core";
import {
  useWorldBuilder,
  MAX_HEIGHT,
  MAX_WIDTH,
  MAX_FLOORS,
} from "./worldbuilding/utils";
import ListWorldsOverlay from "./WorldManager";
import { postWorld } from "./WorldManager";
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

function WorldBuilder({ upload }) {
  const state = useWorldBuilder(upload);
  const [advanced, setAdvanced] = React.useState(false);
  const [isOverlayOpen, setIsOverlayOpen] = React.useState(false);
  //TODO: Consider moving the export somewhere else?
  return (
    <>
      <ListWorldsOverlay
        isOverlayOpen={isOverlayOpen}
        setIsOverlayOpen={setIsOverlayOpen}
      />
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
            onValueChange={(value) => {
              state.setDimensions({ ...state.dimensions, width: value });
            }}
          />

          <NumericInput
            value={state.dimensions.height}
            style={{ width: "3rem" }}
            max={MAX_HEIGHT}
            min={1}
            onValueChange={(value) => {
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
          height: "50px",
        }}
        className="bp3-navbar"
      >
        <Button
          onClick={() => setIsOverlayOpen(!isOverlayOpen)}
          intent="primary"
          style={{ margin: "10px" }}
        >
          Manage Worlds
        </Button>
        <Button
          onClick={() => postWorld(state)}
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
      </div>
    </>
  );
}

export default WorldBuilderPage;
