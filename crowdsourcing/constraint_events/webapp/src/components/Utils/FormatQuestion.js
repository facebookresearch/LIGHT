import React, {useState,useEffect} from "react";

const FormatQuestion = ({
    question,
    keywords,
    containerStyle
})=>{
    //const [keywordPosition, setKeywordPosition] = useState(0)

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
