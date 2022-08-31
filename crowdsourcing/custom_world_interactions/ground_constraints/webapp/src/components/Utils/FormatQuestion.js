
/*****
 * Copyright (c) Meta Platforms, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

//REACT
import React from "react";

//FormatQuestion- formats question and replaces any # with desired keywords in provided array
const FormatQuestion = ({
    question,// question text
    keywords,// array of strings that will replace each # in question text
    containerStyle// style of container component
})=>{
    let questionArr = question.split(" ");
    let keywordPosition = 0;
    return(
        <div className={containerStyle}>
            {
                questionArr.map((questionPiece,index)=>{
                    if(questionPiece=="#" && keywords[keywordPosition]){
                        let currentKeyword = keywords[keywordPosition]
                        keywordPosition++
                        return (
                        <span key={index} style={{color:currentKeyword.color}}>
                            {`${currentKeyword.item} `}
                        </span>
                        )
                    }
                    return (
                        <span key={index}>
                            {`${questionPiece} `}
                        </span>
                    )
                })
            }
        </div>
    )
}
export default FormatQuestion;
