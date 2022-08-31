
/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

//REACT
import React, { useEffect } from 'react';
//KONVA
import { Rect, Text, Group, Line } from 'react-konva';
//UTILS
import GetFlagDimensions from "../../../../../../../utils/GetFlagDimensions";

const ScaleFlag = ({
    width,//container width
    height,//container height
    id,// flag id
    x,// x axis position
    y,// y axis position
    flagX, // Saved X position
    flagY,// Saved Y position
    label,//  Flag Label text
    showPole, //Boolean value that determins whether or not to show "flag pole"
    poleOffset,// how far the pole and flag are offset depending on their proximity to either of the "soft boundaries"
    isDragging,// boolean value that selects which flag is being dragged
    handleDragStart, // function that handles the initiation of the drag action
    handleDragEnd, //  function that handles the end of the drag action and what happens when a flag is placed.
    dragBoundaryHandler, // function the creates boundaries for the drag action.
    leftSoftBoundary, // the boundary between the scale and the gallery
    rightSoftBoundary // the boundary at the right side of the scale
}) => {
    const FlagDimensions = GetFlagDimensions(label, width, 20, 40);
    const {flagLabel, flagLabelWidth, flagLabelHeight, flagWidth, flagHeight} = FlagDimensions;
    let polePosition = width/2 +poleOffset;

    return (
        <Group
            key={id}
            id={id}
            x={x}
            y={y}
            draggable
            onDragStart={handleDragStart}
            onDragEnd={handleDragEnd}
            dragBoundFunc={dragBoundaryHandler}
        >
            <Line
                points={[polePosition, 0, polePosition, height*2]}
                stroke={showPole || ((flagX-poleOffset)>=leftSoftBoundary) ? "blue" : "white"}
                strokeWidth={5}
                opacity={showPole || ((flagX-poleOffset)>=leftSoftBoundary) ? 1 : 0}
            />
            <Rect
                width={flagWidth}
                height={flagHeight}
                fill="blue"
                opacity={1}
                shadowColor="black"
                shadowBlur={10}
                shadowOpacity={0.6}
                shadowOffsetX={isDragging ? 10 : 5}
                shadowOffsetY={isDragging ? 10 : 5}
                style={{zIndex:"99"}}
                offsetX={(poleOffset )|| 0}
            />
            <Text
                text={flagLabel}
                fontSize={20}
                fontStyle={"bold"}
                width={flagLabelWidth}
                height={flagLabelHeight}
                align={"center"}
                verticalAlign={"middle"}
                fill="white"
                opacity={1}
                shadowOpacity={0.6}
                style={{zIndex:"100"}}
                offsetX={(poleOffset) || 0}
            >
            </Text>
        </Group>
)}

export default ScaleFlag
