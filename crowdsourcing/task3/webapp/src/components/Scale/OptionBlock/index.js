import React from 'react';
import { render } from 'react-dom';
import { Stage, Layer, Rect, Text, Group } from 'react-konva';

function generateShapes() {
  return [...Array(10)].map((_, i) => ({
    id: i.toString(),
    x: 1,
    y: i *10,
    isDragging: false,
  }));
}

const INITIAL_STATE = generateShapes();

const OptionBlock = ({height, width}) => {
  const [optionBlocks, setOptionBlocks] = React.useState(INITIAL_STATE);

  const handleDragStart = (e) => {
    const id = e.target.id();
    setOptionBlocks(
        optionBlocks.map((block) => {
        return {
          ...block,
          isDragging: block.id === id,
        };
      })
    );
  };
  const handleDragEnd = (e) => {
    setOptionBlocks(
        optionBlocks.map((block) => {
        return {
          ...block,
          isDragging: false,
        };
      })
    );
  };

  return (
    <>
        <Text text="Try to drag a block" />
        {optionBlocks.map((block) => (
            <Group
            key={block.id}
            id={block.id}
            x={block.x}
            y={block.y}
            draggable
            onDragStart={handleDragStart}
            onDragEnd={handleDragEnd}
            >
                <Rect
                width={100}
                height={100}
                fill="red"
                opacity={0.8}
                shadowColor="black"
                shadowBlur={10}
                shadowOpacity={0.6}
                shadowOffsetX={block.isDragging ? 10 : 5}
                shadowOffsetY={block.isDragging ? 10 : 5}
                scaleX={block.isDragging ? 1.2 : 1}
                scaleY={block.isDragging ? 1.2 : 1}
                />
                <Text
                    text="BLOCK LABEL"
                    fontSize={20}
                    width={100}
                    height={100}
                    align={"center"}
                    fill="white"
                    opacity={0.8}
                    shadowOpacity={0.6}
                    scaleX={block.isDragging ? 1.2 : 1}
                    scaleY={block.isDragging ? 1.2 : 1}
                    style={{zIndex:"100"}}
                >
                </Text>
            </Group>
        ))}
    </>
  );
};

export default OptionBlock
