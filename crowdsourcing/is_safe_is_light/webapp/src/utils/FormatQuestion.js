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
