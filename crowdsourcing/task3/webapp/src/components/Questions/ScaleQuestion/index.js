import React, {useState} from "react";

import "./styles.css"
//CUSTOM COMPONENTS
import Scale from "./Scale";

const DummyData = {
    trait:{
        name:"Strength",
        scale:{
            bottom:{
                name: "Rat"
            },
            mid:{
                name: "Peasant"
            },
            top:{
                name: "Dragon"
            }
        }
    },
    options:[
        "Butcher",
        "Baker",
        "Candlestick Maker",
        "Kroktar Devourer of Souls"
    ]
}
const ScaleQuestion = ({

})=>{

    return(
        <div className="scalequestion-container">
            <Scale
                trait={DummyData.trait}
                actors={DummyData.options}
            />
        </div>
    )
}
export default ScaleQuestion;
