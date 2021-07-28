//REACT
import React, { useEffect } from 'react';
//KONVA
import { Layer, Rect, Text, Group, Line } from 'react-konva';
//CUSTOM COMPONENTS
import SelectionGallery from "./SelectionGallery"
import ExampleFlag from "./ExampleFlag";

//ScaleField - Primary componenent that acts as the field the scaleFlags can moved around on.
const ScaleField = ({
    height,//component Height
    width,// component width
    selection, // array of objects being rated
    scaleRange,// The example objects and colors for the rating scale
}) => {
    const generateFlags = (arr)=> {
        const xPos = (width*.06);//initial position of
        if(arr){
            return [...arr.map(
                (flag, i) => ({
                    name:flag.name,
                    id: i.toString(),
                    x: xPos,
                    y: 50+(i*80),
                    isDragging: false,
                    flagX:xPos,
                    flagY:50+(i*80)
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
    const rightSoftBoundary = scaleContainerWidth+(flagWidth/2);
    const scaleHeaderWidth = width-leftSoftBoundary
//handleDragStart - Handles Dragging event updating dragged flag's information in state.
    const handleDragStart = (e) => {
        const id = e.target.id();
        setSelectionFlags(
            selectionFlags.map((flag) => {
            return {
            ...flag,
            isDragging: flag.id === id,
            showPole:flag.id === id
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
    let leftBoundaryCrossed =(leftEdge - leftSoftBoundary);//space left edge of flag has passed the left soft boundary.
    let rightBoundaryCrossed =(rightEdge-rightSoftBoundary);//space right edge of flag has passed the right soft boundary.
    const leftBoundaryOffset = (leftEdge <leftSoftBoundary) && ((leftEdge-leftBoundaryCrossed)<=(leftEdge+(flagWidth/2)+leftBoundaryCrossed)) ? leftBoundaryCrossed: 0;// ternary that limits when offset of left boundary is applied
    const rightBoundaryOffset = rightEdge>rightSoftBoundary ? rightBoundaryCrossed/2: 0;// ternary that limits when offset of right boundary is applied
    const poleOffset = rightBoundaryOffset + leftBoundaryOffset;// xoffset applied to "flag" and "flag pole"
    const polePosition = flagX+(flagWidth*.5)+poleOffset; //Flag pole position on scale after offset
    let showPole = ((leftEdge-leftBoundaryCrossed)<=(leftEdge+(flagWidth/2)+leftBoundaryCrossed)) ? true :false // ternary that sets the condition of when the "flag pole" is visible
    let ratingValue = ((polePosition-leftSoftBoundary)/(width-leftSoftBoundary))  // value being sent to payload state.
        setSelectionFlags(
            selectionFlags.map((flag) => {
                if(flag.id=== id){
                    return {
                        ...flag,
                        isDragging: false,
                        showPole:showPole,
                        flagX:flagX,
                        flagY:flagY,
                        poleOffset:poleOffset,
                        rating:ratingValue
                    };
                }else{
                    return {
                    ...flag,
                    isDragging: false,
                    showPole:flag.id === id,
                    };
                }
            })
        );
};
const dragBoundaryHandler = (pos)=>{
    const{x, y}= pos;//cursor position during drag event
    const flagX = x;
    const flagY = y;
    const leftXBoundary = 0;
    const rightXBoundary = scaleContainerWidth;
    const topYBoundary = 0;
    const bottomYBoundary = height - 50// 50 is rect Rect height
    let newflagX = flagX < leftXBoundary ? leftXBoundary : ((flagX>rightXBoundary) ? rightXBoundary :flagX);//ternary setting the conditions that define the drag boundary for the X axis
    let newflagY = flagY < topYBoundary ? topYBoundary : ((flagY>bottomYBoundary)? bottomYBoundary :flagY);//ternary setting the conditions that define the drag boundary for the Y axis
    return {
        x: newflagX,
        y: newflagY,
      };
}

  return (
    <Layer>
        <Group
            x={width*.253}
            y={0}
        >
            <Rect
                width={scaleHeaderWidth}
                height={40}
                fill="blue"
                opacity={1}
                shadowColor="black"
                style={{zIndex:"98"}}
            />
            <Rect
                width={scaleHeaderWidth-(scaleHeaderWidth*.1)}
                height={20}
                fill="white"
                opacity={1}
                style={{zIndex:"99"}}
                offsetX={scaleHeaderWidth*-.010}
                offsetY={-10}
            />
            <Text
                text={"Rating Scale"}
                fontSize={20}
                fontStyle={"bold"}
                width={scaleHeaderWidth-(scaleHeaderWidth*.1)}
                height={20}
                align={"center"}
                verticalAlign={"middle"}
                fill="blue"
                opacity={1}
                style={{zIndex:"100"}}
                offsetX={scaleHeaderWidth*-.010}
                offsetY={-10}
            />
        </Group>
        <SelectionGallery
            width={width*.252}
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

    {
    scaleRange.map((section, index)=>{
        const {example, color} = section;//color and example name for example flag component
        let flagSpacing = width*.23;//space between example flags
        let flagWidth = (width/(scaleRange.length)) -flagSpacing
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

export default ScaleField;
