/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

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
                    const {primary, primary_desc, secondary, secondary_desc, narration} = example
                    return(
                        <ExampleCard
                            key={index}
                            primary={primary}
                            primary_desc={primary_desc}
                            secondary={secondary}
                            secondary_desc={secondary_desc}
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
