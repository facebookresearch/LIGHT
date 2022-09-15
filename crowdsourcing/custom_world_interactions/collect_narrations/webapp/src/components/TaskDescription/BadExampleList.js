import React from "react";
//COPY
import {BadExamples} from "./Copy/ExamplesCopy"
//CUSTOM COMPONENTS
import ExampleCard from "../ExampleCard";

const BadExampleList = ()=>{
    return(
        <div className="list-container" style={{borderColor:"red"}}>
            <div className="list-header" style={{backgroundColor:"red"}}>
                <p className="list-header__text">
                    BAD EXAMPLES
                </p>
            </div>
            {
                BadExamples.map((example, index)=>{
                    const {primary, primary_desc, secondary, secondary_desc, action_phrase, narration, badReason} = example
                    return(
                        <ExampleCard
                            key={index}
                            primary={primary}
                            primary_desc={primary_desc}
                            secondary={secondary}
                            secondary_desc={secondary_desc}
                            action_phrase={action_phrase}
                            narration={narration}
                            badReason={badReason}
                        />
                    )
                }

                )
            }
        </div>
    )
}
export default BadExampleList;
