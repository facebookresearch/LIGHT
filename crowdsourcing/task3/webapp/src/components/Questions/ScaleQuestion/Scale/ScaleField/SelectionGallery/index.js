//REACT
import React, { useEffect } from 'react';
//CUSTOM COMPONENTS
import ScaleFlag from "./ScaleFlag"


const SelectionGallery = ({
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
        {selection.map((selectionFlag, i) => {
            const {
                id,
                x,
                y,
                flagX,
                flagY,
                drawLine,
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
                    drawLine={drawLine}
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
