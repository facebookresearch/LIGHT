/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

//FormatQuestion - component that takes a string and replaces # with dynamic keywords
const FormatQuestion = (
    question,
    keywords,
)=>{
    let updatedQuestionStr = "";
    let unupdatedQuestionArr = question.split(" ");
    let updatedQuestionArr ;
    let keywordPosition = 0;
    updatedQuestionArr = unupdatedQuestionArr.map((questionPiece,index)=>{
        if(questionPiece=="#" && keywords[keywordPosition]){
            let currentKeyword = keywords[keywordPosition]
            keywordPosition++
            return (
                `${currentKeyword} `
            )
        }
        return (
                `${questionPiece} `
        )
    });
    updatedQuestionStr = updatedQuestionArr.join(" ");
    return updatedQuestionStr;
}
export default FormatQuestion;
