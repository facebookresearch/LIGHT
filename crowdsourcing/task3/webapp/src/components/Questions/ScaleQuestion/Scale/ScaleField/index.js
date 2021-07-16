//REACT
import React, { useEffect } from 'react';
//KONVA
import { Layer, Rect, Text, Group, Line } from 'react-konva';
//CUSTOM COMPONENTS
import ExampleFlag from "../ExampleFlag";

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

const ScaleField = ({
    height,
    width,
    selection,
    scaleRange
    // leftSoftBoundary,
    // rightSoftBoundary,
}) => {
    const [scaleContainerWidth, setScaleContainerWidth] = React.useState(0)
    const [optionBlocks, setOptionBlocks] = React.useState([]);
    useEffect(()=>{
        setScaleContainerWidth(width*.8)
    },[width])
    useEffect(()=>{
        if(selection){
            let updatedBlocks = generateShapes(selection);
            setOptionBlocks(updatedBlocks);
        }
    },[selection])
    const flagWidth = width*.10;
    const flagHeight = 50;
    const polePosition = flagWidth/2
    const leftSoftBoundary = (width*.235)
    const rightSoftBoundary = width-(width*.05);

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
//handleDragEnd - invoked at the end of the dragging event.
  const handleDragEnd = (e) => {
    const id = e.target.id();//id of the flag
    const blockX = e.target.x();//flag's x coordinates
    const blockY = e.target.y();//flag's y coordinates
    const leftEdge= blockX;//Left edge of flag
    const rightEdge= blockX+flagWidth// Right edge of flag
    const leftBoundaryOffset = (leftEdge<leftSoftBoundary && (leftEdge+(flagWidth/2))>leftSoftBoundary) ? leftEdge -leftSoftBoundary: 0;
    const rightBoundaryOffset = rightEdge>rightSoftBoundary ? rightEdge-rightSoftBoundary : 0;
    console.log("LEFT SOFTBOUNDARY:  ", leftSoftBoundary)
    console.log("RIGHT SOFTBOUNDARY:  ", rightSoftBoundary)
    console.log("LEFT BOUNDARY OFFSET:  ", leftBoundaryOffset, leftEdge<leftSoftBoundary)
    console.log("RIGHT BOUNDARY OFFSET:  ", rightBoundaryOffset, rightEdge>rightSoftBoundary )
    const poleOffset = rightBoundaryOffset + leftBoundaryOffset;
    console.log("OFFSET ", poleOffset)
    console.log("X", blockX)
    console.log("Y", blockY)
        setOptionBlocks(
            optionBlocks.map((block) => {
                if(block.id=== id){
                    return {
                        ...block,
                        isDragging: false,
                        drawLine:blockX  > leftSoftBoundary,
                        blockX:blockX,
                        blockY:blockY,
                        poleOffset:poleOffset

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
    <Layer width={scaleContainerWidth}>
        <Line
            points={[width*.252, 0, width*.253, height]}
            stroke={"blue"}
            strokeWidth={5}
        />
        {optionBlocks.map((block, i) => {
            console.log("BLOCK #", i, "  ", block)
            const {
                id,
                x,
                y,
                blockX,
                blockY,
                drawLine,
                poleOffset,
                isDragging,
                name
            } = block;

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
                    stroke={(drawLine||(blockX  > leftSoftBoundary)) ? "blue" : "white"}
                    strokeWidth={5}
                    opacity={(drawLine||(blockX > leftSoftBoundary)) ? 1 : 0}
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
                    offsetX={(poleOffset/2 )|| 0}
                />
                <Text
                    text={name}
                    fontSize={12}
                    fontStyle={"bold"}
                    width={width*.10}
                    height={flagHeight}
                    align={"center"}
                    verticalAlign={"middle"}
                    fill="white"
                    opacity={0.8}
                    shadowOpacity={0.6}
                    style={{zIndex:"100"}}
                    offsetX={(poleOffset/2) || 0}
                >
                </Text>
            </Group>
        )}
    )}
    {
    scaleRange.map((section, index)=>{
        const {example, color} = section;
        let xOffset =(width*.27);
        let xPosition = ((width*.23)*index) + xOffset;
        return(
            <ExampleFlag
                key={index}
                xPosition={xPosition}
                yPosition={200}
                width={width}
                height={height}
                label={example}
                color={color}
            />
        )})
    }
        <Line
            x={width*.253}
            y={height}
            points={[0, 0, width, 0, width, height*-.15]}
            tension={0}
            closed
            stroke="black"
            fillLinearGradientStartPoint={{ x: 0, y: 0 }}
            fillLinearGradientEndPoint={{ x: width*.13, y: height*-.075 }}
            fillLinearGradientStartPoint={{ x: width*.13, y: height*-.075 }}
            fillLinearGradientEndPoint={{ x: width*.6, y: height*-.15 }}
            fillLinearGradientColorStops={[0, 'green', 0.3, "blue", 1, 'red']}
        />
    </Layer>
  );
};

export default ScaleField
