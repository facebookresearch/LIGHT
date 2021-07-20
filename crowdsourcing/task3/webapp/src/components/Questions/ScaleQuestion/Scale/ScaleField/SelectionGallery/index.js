//REACT
import React, { useEffect } from 'react';
//KONVA
import {Rect, Text, Group} from 'react-konva';
//CUSTOM COMPONENTS
import ScaleFlag from "./ScaleFlag"


const SelectionGallery = ({
    width,
    height,
    flagWidth,
    selection,
    handleDragStart,
    handleDragEnd,
    dragBoundaryHandler,
    leftSoftBoundary,
    rightSoftBoundary,
}) => {

  return (
    <>
        <Group
            x={0}
            y={0}
        >
            <Rect
                width={width}
                height={40}
                fill="blue"
                opacity={1}
                shadowColor="black"
                style={{zIndex:"98"}}
            />
            <Rect
                width={width-(width*.2)}
                height={20}
                fill="white"
                opacity={1}
                style={{zIndex:"99"}}
                offsetX={width*-.1}
                offsetY={-10}
            />
            <Text
                text={"Selection"}
                fontSize={20}
                fontStyle={"bold"}
                width={width-(width*.2)}
                height={20}
                align={"center"}
                verticalAlign={"middle"}
                fill="blue"
                opacity={1}
                style={{zIndex:"100"}}
                offsetX={width*-.025}
                offsetY={-10}
            >
            </Text>
        </Group>
        {selection.map((selectionFlag, i) => {
            const {
                id,
                x,
                y,
                flagX,
                flagY,
                showPole,
                poleOffset,
                isDragging,
                name,
            } = selectionFlag;

            return (
                <ScaleFlag
                    key={id}
                    width={flagWidth}
                    height={height}
                    id={id}
                    x={x}
                    y={y}
                    flagX={flagX}
                    flagY={flagY}
                    label={name}
                    showPole={showPole}
                    poleOffset={poleOffset}
                    isDragging={isDragging}
                    handleDragStart={handleDragStart}
                    handleDragEnd={handleDragEnd}
                    dragBoundaryHandler={dragBoundaryHandler}
                    leftSoftBoundary={leftSoftBoundary}
                    rightSoftBoundary={rightSoftBoundary}
                />
            )}
        )}
    </>
  );
};

export default SelectionGallery
