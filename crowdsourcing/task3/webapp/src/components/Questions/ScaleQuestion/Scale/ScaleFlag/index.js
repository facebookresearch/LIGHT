//REACT
import React, {useState} from "react";
//KONVA
import { Rect, Text, Group, Line } from 'react-konva';
//STYLING
import "./styles.css"


const ScaleFlag = ({
    xPosition,
    yPosition,
    width,
    height,
    label,
    color
}) => {

return (
    <Group
        x={xPosition}
        y={yPosition}
    >
        <Line
            points={[width*.075, 0, width*.075, height*2]}
            stroke= {color>1? "red": color>0 ? "blue": "green"}
            strokeWidth={5}
        />

        <Rect
            width={width*.15}
            height={50}
            fill={color>1? "red": color>0 ? "blue": "green"}
            opacity={1}
            shadowColor="black"
            shadowBlur={10}
            shadowOpacity={0.6}
        />
        <Rect
            width={width*.13}
            height={40}
            offsetX={width*-.01}
            offsetY={-5}
            fill="white"
            opacity={1}
            shadowColor="black"
            shadowBlur={10}
            shadowOpacity={0.6}
        />
        <Text
            text={label}
            fontSize={20}
            width={width*.13}
            height={50}
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
export default ScaleFlag;
