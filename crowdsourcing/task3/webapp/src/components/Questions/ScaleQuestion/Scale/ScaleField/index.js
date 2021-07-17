//REACT
import React, { useEffect } from 'react';
//KONVA
import { Layer, Rect, Text, Group, Line } from 'react-konva';
//CUSTOM COMPONENTS
import SelectionGallery from "./SelectionGallery"
import ExampleFlag from "./ExampleFlag";

//ScaleField - Primary componenent that acts as the field the scaleFlags can moved around on.
const ScaleField = ({
    height,
    width,
    selection,
    scaleRange,
}) => {
    const generateFlags = (arr)=> {
        const xPos = (width*.253)*.3;
        if(arr){
            return [...arr.map(
                (name, i) => ({
                    name:name,
                    id: i.toString(),
                    x: xPos,
                    y: 25+(i*80),
                    isDragging: false,
                    })
                )
            ];
        }
    }
/**************************STATE***************************************************************/
    const [scaleContainerWidth, setScaleContainerWidth] = React.useState(0)//containerwidth of entire field
    const [selectionFlags, setSelectionFlags] = React.useState([]);//Array of objects being rated

    useEffect(()=>{
        setScaleContainerWidth(width*.8)
    },[width])

    useEffect(()=>{
        if(selection){
            let updatedSelectionFlags = generateFlags(selection);
            setSelectionFlags(updatedSelectionFlags);
        }
    },[selection])

    const flagWidth = width*.1;
    const leftSoftBoundary = (width*.253);
    const rightSoftBoundary = scaleContainerWidth

    const handleDragStart = (e) => {
        const id = e.target.id();
        console.log(e.target)
        setSelectionFlags(
            selectionFlags.map((flag) => {
            return {
            ...flag,
            isDragging: flag.id === id,
            drawLine:flag.id === id
            };
        }));
    };
//handleDragEnd - invoked at the end of the dragging event.
  const handleDragEnd = (e) => {
    const id = e.target.id();//id of the flag
    const flagX = e.target.x();//flag's x coordinates
    const flagY = e.target.y();//flag's y coordinates
    const leftEdge= flagX;//Left edge of flag

    const rightEdge= flagX+flagWidth// Right edge of flag
    const leftBoundaryOffset = (leftEdge<leftSoftBoundary && (leftEdge+(flagWidth/2))>leftSoftBoundary) ? leftEdge -leftSoftBoundary: 0;
    const rightBoundaryOffset = rightEdge>rightSoftBoundary ? (rightEdge-rightSoftBoundary)/2 : 0;
    console.log("LEFT SOFTBOUNDARY:  ", leftSoftBoundary)
    console.log("RIGHT SOFTBOUNDARY:  ", rightSoftBoundary)
    console.log("LEFT BOUNDARY OFFSET:  ", leftBoundaryOffset, leftEdge<leftSoftBoundary)
    console.log("RIGHT BOUNDARY OFFSET:  ", rightBoundaryOffset, rightEdge>rightSoftBoundary )
    const polePosition = flagX+(flagWidth/2);
    const poleOffset = rightBoundaryOffset + leftBoundaryOffset;
    console.log("OFFSET ", poleOffset)
    console.log("X", flagX)
    console.log("Y", flagY)
        setSelectionFlags(
            selectionFlags.map((flag) => {
                if(flag.id=== id){
                    return {
                        ...flag,
                        isDragging: false,
                        drawLine:polePosition > leftSoftBoundary,
                        flagX:flagX,
                        flagY:flagY,
                        poleOffset:poleOffset

                    };
                }else{
                    return {
                    ...flag,
                    isDragging: false,
                    drawLine:flag.id === id,
                    };
                }
            })
        );
};
const dragBoundaryHandler = (pos)=>{
    const{x, y}= pos
    let polePosition = flagWidth/2
    const flagX = x;
    const flagY = y;
    const leftXBoundary = 0;
    const rightXBoundary = scaleContainerWidth;
    const topYBoundary = 0;
    const bottomYBoundary = height - 50// 50 is rect Rect height
    let newflagX = flagX < leftXBoundary ? leftXBoundary : ((flagX+flagWidth)>rightXBoundary) ? rightXBoundary :flagX;
    let newflagY = flagY < topYBoundary ? topYBoundary : flagY>bottomYBoundary ? bottomYBoundary :flagY;
    return {
        x: newflagX,
        y: newflagY,
      };
}

  return (
    <Layer>
        <SelectionGallery
            height={height}
            flagWidth={flagWidth}
            selection={selectionFlags}
            handleDragStart={handleDragStart}
            handleDragEnd={handleDragEnd}
            dragBoundaryHandler={dragBoundaryHandler}
            leftSoftBoundary={leftSoftBoundary}
            rightSoftBoundary={leftSoftBoundary}
        />
        <Line
            points={[leftSoftBoundary, 0, leftSoftBoundary, height]}
            stroke={"blue"}
            strokeWidth={5}
        />
        <Line
            points={[scaleContainerWidth, 0, scaleContainerWidth, height]}
            stroke={"blue"}
            strokeWidth={5}
        />
    {
    scaleRange.map((section, index)=>{
        const {example, color} = section;
        let flagSpacing = width*.23;
        let flagWidth = (width/(scaleRange.length)) -flagSpacing
        console.log("FLAG DIMENSIONS", flagSpacing, flagWidth)
        let xOffset =(width*.27);
        let xPosition = ((width*.23)*index) + xOffset;
        return(
            <ExampleFlag
                key={index}
                xPosition={xPosition}
                yPosition={200}
                width={flagWidth}
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







// <Layer width={scaleContainerWidth}>
// <Line
//     points={[width*.252, 0, width*.253, height]}
//     stroke={"blue"}
//     strokeWidth={5}
// />
// <SelectionGallery
//     height={height}
//     width={width}
//     selection={selection}
//     handleDragStart={handleDragStart}
//     handleDragEnd={handleDragEnd}
//     leftSoftBoundary={leftSoftBoundary}
//     rightSoftBoundary={leftSoftBoundary}
// />
// {selectionFlags.map((flag, i) => {
//     console.log("flag #", i, "  ", flag)
//     const {
//         id,
//         x,
//         y,
//         flagX,
//         flagY,
//         drawLine,
//         poleOffset,
//         isDragging,
//         name
//     } = flag;

//     return (
//     <Group
//         key={id}
//         id={id}
//         x={x}
//         y={y}
//         draggable
//         onDragStart={handleDragStart}
//         onDragEnd={handleDragEnd}
//         dragBoundFunc={dragBoundaryHandler}
//     >
//         <Line
//             points={[polePosition, 0, polePosition, height*2]}
//             stroke={(drawLine||(flagX  > leftSoftBoundary)) ? "blue" : "white"}
//             strokeWidth={5}
//             opacity={(drawLine||(flagX > leftSoftBoundary)) ? 1 : 0}
//         />

//         <Rect
//             width={flagWidth}
//             height={flagHeight}
//             fill="blue"
//             opacity={1}
//             shadowColor="black"
//             shadowBlur={10}
//             shadowOpacity={0.6}
//             shadowOffsetX={isDragging ? 10 : 5}
//             shadowOffsetY={isDragging ? 10 : 5}
//             style={{zIndex:"99"}}
//             offsetX={(poleOffset/2 )|| 0}
//         />
//         <Text
//             text={name}
//             fontSize={12}
//             fontStyle={"bold"}
//             width={width*.10}
//             height={flagHeight}
//             align={"center"}
//             verticalAlign={"middle"}
//             fill="white"
//             opacity={0.8}
//             shadowOpacity={0.6}
//             style={{zIndex:"100"}}
//             offsetX={(poleOffset/2) || 0}
//         >
//         </Text>
//     </Group>
// )}
// )}
// {
// scaleRange.map((section, index)=>{
// const {example, color} = section;
// let flagSpacing = width*.23;
// let flagWidth = (width/(scaleRange.length)) -flagSpacing
// console.log("FLAG DIMENSIONS", flagSpacing, flagWidth)
// let xOffset =(width*.27);
// let xPosition = ((width*.23)*index) + xOffset;
// return(
//     <ExampleFlag
//         key={index}
//         xPosition={xPosition}
//         yPosition={200}
//         width={flagWidth}
//         height={height}
//         label={example}
//         color={color}
//     />
// )})
// }
// <Line
//     x={width*.253}
//     y={height}
//     points={[0, 0, width, 0, width, height*-.15]}
//     tension={0}
//     closed
//     stroke="black"
//     fillLinearGradientStartPoint={{ x: 0, y: 0 }}
//     fillLinearGradientEndPoint={{ x: width*.13, y: height*-.075 }}
//     fillLinearGradientStartPoint={{ x: width*.13, y: height*-.075 }}
//     fillLinearGradientEndPoint={{ x: width*.6, y: height*-.15 }}
//     fillLinearGradientColorStops={[0, 'green', 0.3, "blue", 1, 'red']}
// />
// </Layer>
