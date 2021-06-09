import React, {useState} from "react";

const FormatQuestion = ({
    question,
    keywords,
    containerStyle
})=>{
    let questionArr = question.split(" ");
    let keywordsArr = keywords;
    return(
        <div className={containerStyle}>
            {
                questionArr.map((questionPiece,index)=>{
                    if(questionPiece=="#" && keywordsArr[0]){
                        let currentKeyword = keywordsArr[0]
                        keywordsArr.shift()
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
