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
                    const {primary, primary_desc, secondary, secondary_desc, action_phrase, narration} = example
                    return(
                        <ExampleCard
                            key={index}
                            primary={primary}
                            primary_desc={primary_desc}
                            secondary={secondary}
                            secondary_desc={secondary_desc}
                            action_phrase={action_phrase}
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
