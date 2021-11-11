/* REACT */
import React, {useEffect} from 'react';
import { useParams, useRouteMatch, useHistory } from "react-router-dom";
/* REDUX */
import {useAppDispatch, useAppSelector} from '../../app/hooks';
/* CUSTOM COMPONENTS */
import Grid from "./Grid"
/* BLUEPRINT JS COMPONENTS */
import {
    NumericInput,
    InputGroup,
    ControlGroup,
    FormGroup,
    Tooltip,
    Position,
    Icon,
    Switch,
    Button,
    Intent,
  } from "@blueprintjs/core";
/* STYLES */


const STARTING_WIDTH = 5;
const STARTING_HEIGHT = 5;
const STARTING_FLOORS = 1;

const SIZE = 150;
const MARGIN = 24;

const WorldBuilderMap2 = ()=> {
    const [dimensions, setDimensions] = React.useState( 
        {
            name: null,
            height: STARTING_HEIGHT,
            width: STARTING_WIDTH,
            floors: STARTING_FLOORS,
        }
    );
    return(
    <div
        style={{
          width:
            dimensions.width * SIZE +
            (dimensions.width + 1) * MARGIN +
            60,
          margin: "0 auto 75px auto",
          textAlign: "center",
        }}
    >
        <Button
            className="bp3-button"
            style={{
            width:
                dimensions.width * SIZE +
                (dimensions.width + 1) * MARGIN -
                20,
            margin: "auto",
            }}
            icon="arrow-up"
        />
        <div style={{ display: "flex" }}>
            <Button
                className="bp3-button"
                style={{
                height:
                    dimensions.height * SIZE +
                    (dimensions.height + 1) * MARGIN -
                    20,
                margin: "10px 0",
                }}
                icon="arrow-left"
            />
            <div
                className="map-container"
                style={{
                width:
                    dimensions.width * SIZE +
                    (dimensions.width + 1) * MARGIN,
                height:
                    dimensions.height * SIZE +
                    (dimensions.height + 1) * MARGIN,
                }}
            >
                <Grid
                    dimensions={dimensions}
                />
        </div>
        <Button
            className="bp3-button"
            style={{
              height:
                dimensions.height * SIZE +
                (dimensions.height + 1) * MARGIN -
                20,
              margin: "10px 0",
            }}
            icon="arrow-right"
          />
        </div>
        <Button
          className="bp3-button"
          style={{
            width:
              dimensions.width * SIZE +
              (dimensions.width + 1) * MARGIN -
              20,
            margin: "auto",
          }}
          icon="arrow-down"
        />
      </div>
    )
}

export default WorldBuilderMap2;