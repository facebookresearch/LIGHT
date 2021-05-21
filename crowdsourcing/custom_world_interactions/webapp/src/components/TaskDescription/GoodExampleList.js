import React from "react";
//COPY
import {GoodExamples} from "./Copy/ExamplesCopy"
//CUSTOM COMPONENTS
import ExampleCard from "../ExampleCard";

const GoodExampleList = ()=>{
    return(
        <div className="list-container" style={{borderColor:"green"}}>
            <div className="list-header" style={{backgroundColor:"green"}}>
                <p className="list-header__text">
                    GOOD EXAMPLES
                </p>
            </div>
            {
                GoodExamples.map((example, index)=>{
                    const {primary, secondary, narration} = example
                    return(
                        <ExampleCard
                            key={index}
                            primary={primary}
                            secondary={secondary}
                            narration={narration}
                        />
                    )
                }

                )
            }
        </div>
    )
}
export default GoodExampleList;
