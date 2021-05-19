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
                    Bad EXAMPLES
                </p>
            </div>
            {
                BadExamples.map((example, index)=>{
                    const {primary, secondary, narration, badReason} = example
                    return(
                        <ExampleCard
                            key={index}
                            primary={primary}
                            secondary={secondary}
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
