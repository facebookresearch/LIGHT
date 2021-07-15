//REACT
import React, { useEffect } from 'react';
//KONVA
import { Rect, Text, Group, Line } from 'react-konva';


const ScaleFlag = ({
    height,
    width,
    actors,
    boundary
}) => {


  return (
            <Group
            key={block.id}
            id={block.id}
            x={block.x}
            y={block.y}
            draggable
            onDragStart={handleDragStart}
            onDragEnd={handleDragEnd}
        >
            <Line
                points={[block.x+width*.08, 0, block.x+width*.08, height*2]}
                stroke={(block.drawLine||(block.blockX  > width*.252)) ? "blue" : "white"}
                strokeWidth={5}
                opacity={(block.drawLine||(block.blockX > width*.252)) ? 1 : 0}
            />

            <Rect
                width={width*.20}
                height={50}
                fill="blue"
                opacity={1}
                shadowColor="black"
                shadowBlur={10}
                shadowOpacity={0.6}
                shadowOffsetX={block.isDragging ? 10 : 5}
                shadowOffsetY={block.isDragging ? 10 : 5}
                scaleX={block.isDragging ? 1.2 : 1}
                scaleY={block.isDragging ? 1.2 : 1}
            />
            <Text
                text={block.name}
                fontSize={20}
                width={width*.20}
                height={50}
                align={"center"}
                verticalAlign={"middle"}
                fill="white"
                opacity={0.8}
                shadowOpacity={0.6}
                scaleX={block.isDragging ? 1.2 : 1}
                scaleY={block.isDragging ? 1.2 : 1}
                style={{zIndex:"100"}}
            >
            </Text>
        </Group>
)}

export default ScaleFlag
