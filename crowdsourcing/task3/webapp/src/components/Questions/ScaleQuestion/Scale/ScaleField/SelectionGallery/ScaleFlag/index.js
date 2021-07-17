//REACT
import React, { useEffect } from 'react';
//KONVA
import { Rect, Text, Group, Line } from 'react-konva';
//UTILS
import GetFlagDimensions from "../../../../../../../utils/GetFlagDimensions";

const ScaleFlag = ({
    width,
    height,
    id,
    x,
    y,
    flagX,
    flagY,
    label,
    drawLine,
    poleOffset,
    isDragging,
    handleDragStart,
    handleDragEnd,
    dragBoundaryHandler,
    leftSoftBoundary,
    rightSoftBoundary,
}) => {
    const FlagDimensions = GetFlagDimensions(label, width, 10, 40);
    console.log("FLAG DIMENSIONS:  ", FlagDimensions)
    const {flagLabel, flagLabelWidth, flagLabelHeight, flagWidth, flagHeight} = FlagDimensions;
    const polePosition = flagWidth/2;
    console.log("flagX:  ", flagX)
    console.log("flagY:  ", flagY)
    console.log("polePosition:  ", polePosition)
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
                stroke={(drawLine||(flagX  > leftSoftBoundary)) ? "blue" : "white"}
                strokeWidth={5}
                opacity={(drawLine||(flagX > leftSoftBoundary)) ? 1 : 0}
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
