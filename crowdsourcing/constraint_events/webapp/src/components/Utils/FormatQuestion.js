import React, {useState} from "react";

import "./styles.css"

const FormatQuestion = ({
    question, keywords, containterStyle
})=>{
    let questionArr = question.split(" ")
    let keywordsArr = keywords;
    return(
        <div className={containterStyle}>
            {
                questionArr.map((questionPiece,index)=>{
                    if(questionPiece=="#"){
                        let currentKeyword = keywordsArr[0]
                        keywordsArr.shift()
                        return (
                        <span key={index} style={{color:currentKeyword.color}}>
                            {currentKeyword.item}
                        </span>
                        )
                    }
                    return (
                        <span key={index}>
                            {questionPiece}
                        </span>
                    )
                })
            }
        </div>
    )
}
export default FormatQuestion;
