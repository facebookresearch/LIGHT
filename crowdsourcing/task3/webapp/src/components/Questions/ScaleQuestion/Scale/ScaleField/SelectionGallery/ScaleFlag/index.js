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
    rightSoftBoundary
}) => {
    const FlagDimensions = GetFlagDimensions(label, width, 20, 40);
    const {flagLabel, flagLabelWidth, flagLabelHeight, flagWidth, flagHeight} = FlagDimensions;
    let polePosition = width/2 +poleOffset;
    console.log("LEFT SOFT boundary  :", leftSoftBoundary)
    console.log("flagX+ offset:  ", flagX-poleOffset)
    console.log("SHOW POLE IN FLAG COMPONENT", flagX-poleOffset>leftSoftBoundary)
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
                points={[0, 0, 0, height*2]}
                stroke={ "green"}
                strokeWidth={5}
                opacity={1}
            />
            <Line
                points={[polePosition, 0, polePosition, height*2]}
                stroke={drawLine || ((flagX-poleOffset)>=leftSoftBoundary) ? "blue" : "white"}
                strokeWidth={5}
                opacity={drawLine || ((flagX-poleOffset)>=leftSoftBoundary) ? 1 : 0}
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
