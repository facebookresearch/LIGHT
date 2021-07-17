//REACT
import React, {useState} from "react";
//KONVA
import { Rect, Text, Group, Line } from 'react-konva';
//STYLING
import "./styles.css";
//UTILS
import GetFlagDimensions from "../../../../../../utils/GetFlagDimensions";

const ExampleFlag = ({
    xPosition,
    yPosition,
    width,
    height,
    label,
    color
}) => {
const FlagDimensions = GetFlagDimensions(label, width, 10, 40);
const {flagLabel, flagLabelWidth, flagLabelHeight, flagWidth, flagHeight} = FlagDimensions;
const flagXOffset = (flagLabelWidth-flagWidth)/2;
const flagYOffset = (flagLabelHeight -flagHeight)/2;
const polePosition = flagWidth/2;
return (
    <Group
        x={xPosition}
        y={yPosition}
    >
        <Line
            points={[polePosition, 0, polePosition, height*2]}
            stroke= {color}
            strokeWidth={5}
        />

        <Rect
            width={flagWidth}
            height={flagHeight}
            fill={color}
            opacity={1}
            shadowColor="black"
            shadowBlur={10}
            shadowOpacity={0.6}

        />
        <Rect
            width={flagLabelWidth}
            height={flagLabelHeight}
            offsetX={flagXOffset}
            offsetY={flagYOffset}
            fill="white"
        />
        <Text
            text={flagLabel}
            fontSize={18}
            width={flagLabelWidth}
            height={flagLabelHeight}
            offsetX={flagXOffset}
            offsetY={flagYOffset}
            align={"center"}
            verticalAlign={"middle"}
            fill={color}
            opacity={0.8}
            shadowOpacity={0.6}
            style={{zIndex:"100"}}
        >
        </Text>
    </Group>
    )
}
export default ExampleFlag;
