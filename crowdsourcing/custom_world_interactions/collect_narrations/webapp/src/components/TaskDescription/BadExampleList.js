
/*****
 * Copyright (c) Meta Platforms, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

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
                    const {primary, primary_desc, secondary, secondary_desc, narration, badReason} = example
                    return(
                        <ExampleCard
                            key={index}
                            primary={primary}
                            primary_desc={primary_desc}
                            secondary={secondary}
                            secondary_desc={secondary_desc}
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
