//REACT
import React, { useEffect } from 'react';
//KONVA
import { Rect, Text, Group, Line } from 'react-konva';

const generateShapes = (arr)=> {
    if(arr){
        return [...arr.map(
            (name, i) => ({
                name:name,
                id: i.toString(),
                x: 25,
                y: 25+(i*60),
                isDragging: false,
                })
            )
        ];
    }
}

const INITIAL_STATE = generateShapes();

const OptionBlock = ({
    height,
    width,
    actors,
    leftSoftBoundary,
    rightSoftBoundary,
}) => {
    const [optionBlocks, setOptionBlocks] = React.useState([]);
    useEffect(()=>{
        if(actors){
            let updatedBlocks = generateShapes(actors);
            setOptionBlocks(updatedBlocks);
        }
    },[actors])
    const flagWidth = width*.10;
    const flagHeight = 50

    const handleDragStart = (e) => {
        const id = e.target.id();
        console.log(e.target)
        setOptionBlocks(
            optionBlocks.map((block) => {
            return {
            ...block,
            isDragging: block.id === id,
            drawLine:block.id === id
            };
        }));
    };
  const handleDragEnd = (e) => {
    const id = e.target.id();
    const blockX = e.target.x();
    const blockY = e.target.y();
    const boundaryOffset =
    console.log("X", blockX)
    console.log("Y", blockY)
    console.log(e.target)

        setOptionBlocks(
            optionBlocks.map((block) => {
                if(block.id=== id){
                    return {
                        ...block,
                        isDragging: false,
                        drawLine:blockX  > leftSoftBoundary,
                        blockX:blockX,
                        blockY:blockY,
                        truePosition:
                    };
                }else{
                    return {
                    ...block,
                    isDragging: false,
                    drawLine:block.id === id,
                    };
                }
            })
        );
};
const dragBoundaryHandler = (pos)=>{
    const{x, y}= pos
    console.log("DRAG EVENT:  ", pos)
    const blockX = x;
    const blockY = y;
    const leftXBoundary = 0;
    const rightXBoundary = width-(width*.05);
    const topYBoundary = 0;
    const bottomYBoundary = height - 50// 50 is rect Rect height
    console.log("X", blockX)
    console.log("Y", blockY)
    let newBlockX = blockX < leftXBoundary ? leftXBoundary : blockX>rightXBoundary ? rightXBoundary :blockX;
    let newBlockY = blockY < topYBoundary ? topYBoundary : blockY>bottomYBoundary ? bottomYBoundary :blockY;
    return {
        x: newBlockX,
        y: newBlockY,
      };
}

  return (
    <>
        {optionBlocks.map((block, i) => {
            console.log("BLOCK #", i, "  ", block)
            return (
            <Group
                key={block.id}
                id={block.id}
                x={block.x}
                y={block.y}
                draggable
                onDragStart={handleDragStart}
                onDragEnd={handleDragEnd}
                dragBoundFunc={dragBoundaryHandler}
            >
                <Line
                    points={[block.x+width*.05, 0, block.x+width*.05, height*2]}
                    stroke={(block.drawLine||(block.blockX  > width*.252)) ? "blue" : "white"}
                    strokeWidth={5}
                    opacity={(block.drawLine||(block.blockX > width*.252)) ? 1 : 0}
                />

                <Rect
                    width={flagWidth}
                    height={50}
                    fill="blue"
                    opacity={1}
                    shadowColor="black"
                    shadowBlur={10}
                    shadowOpacity={0.6}
                    shadowOffsetX={block.isDragging ? 10 : 5}
                    shadowOffsetY={block.isDragging ? 10 : 5}
                    style={{zIndex:"99"}}
                />
                <Text
                    text={block.name}
                    fontSize={12}
                    fontStyle={"bold"}
                    width={width*.10}
                    height={50}
                    align={"center"}
                    verticalAlign={"middle"}
                    fill="white"
                    opacity={0.8}
                    shadowOpacity={0.6}
                    style={{zIndex:"100"}}
                >
                </Text>
            </Group>
        )}
    )}
    </>
  );
};

export default OptionBlock
