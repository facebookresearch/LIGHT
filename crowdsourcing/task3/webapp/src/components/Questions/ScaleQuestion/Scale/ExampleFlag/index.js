//REACT
import React, {useState} from "react";
//KONVA
import { Rect, Text, Group, Line } from 'react-konva';
//STYLING
import "./styles.css";
//UTILS
import GetFlagDimensions from "../../../../../utils/GetFlagDimensions.js";

const ExampleFlag = ({
    xPosition,
    yPosition,
    width,
    height,
    label,
    color
}) => {
const FlagDimensions = GetFlagDimensions(label, width, 10, 40)
const {flagLabel, flagLabelWidth, flagWidth, flagHeight} = FlagDimensions;
return (
    <Group
        x={xPosition}
        y={yPosition}
    >
        <Line
            points={[width*.05, 0, width*.05, height*2]}
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
            width={flagWidth}
            height={flagHeight}
            offsetX={width*-.005}
            offsetY={-5}
            fill="white"
            opacity={1}
            shadowColor="black"
            shadowBlur={10}
            shadowOpacity={0.6}
        />
        <Text
            text={flagLabel}
            fontSize={18}
            width={flagLabelWidth}
            height={flagHeight}
            offsetX={width*-.01}
            offsetY={-5}
            align={"center"}
            verticalAlign={"middle"}
            fill="red"
            opacity={0.8}
            shadowOpacity={0.6}
            style={{zIndex:"100"}}
        >
        </Text>
    </Group>
    )
}
export default ExampleFlag;
