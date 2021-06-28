import React, { useEffect } from 'react';
import { render } from 'react-dom';
import { Stage, Layer, Rect, Text, Group, Line } from 'react-konva';

const generateShapes = (arr)=> {
    if(arr){
        return [...arr.map(
            (name, i) => ({
                name:name,
                id: i.toString(),
                x: 1,
                y: i*60,
                isDragging: false,
                })
            )
        ];
    }
}

const INITIAL_STATE = generateShapes();

const OptionBlock = ({height, width, actors}) => {
    const [optionBlocks, setOptionBlocks] = React.useState([]);
    useEffect(()=>{
        if(actors){
        let updatedBlocks = generateShapes(actors)
        setOptionBlocks(updatedBlocks)
        }
    },[actors])


    const handleDragStart = (e) => {
    const id = e.target.id();
    setOptionBlocks(
        optionBlocks.map((block) => {
        return {
          ...block,
          isDragging: block.id === id,
          drawLine:"false"
        };
      })
    );
  };
  const handleDragEnd = (e) => {

    console.log(e.target)
    setOptionBlocks(
        optionBlocks.map((block) => {
        return {
            ...block,
            isDragging: false,
            drawLine:true
        };
      })
    );
  };

  return (
    <>
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
                <Line
                points={[block.x+100, 0, block.x+100, 500]}
                stroke={block.drawLine ? "black" : "white"}
                strokeWidth={15}

                />

                <Rect
                width={200}
                height={50}
                fill="blue"
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
                    text={block.name}
                    fontSize={20}
                    width={200}
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
        ))}
    </>
  );
};

export default OptionBlock
