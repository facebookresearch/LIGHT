//GetFlagDimensions - Function that returns an object  with flag styling dimensions and label based on the length of the label text
const GetFlagDimensions = (
    label, //Flag Text
    labelWidth, // ScreenWidth - used to calculate flag width
    rowLength, //Desired number of characters on each row
    rowHeight // Desired heigh of each row
)=>{
    //Default Label Values
    let labelLength = label.length; // Number of characters in label text
    let labelContainerRows=  1 // Default Number of rows
    let labelContainerWidth= labelWidth // default Container width
    if(labelLength>rowLength){
        labelContainerRows=  Math.ceil(labelLength/rowLength);
    }
    let flagWidth = labelContainerWidth*1.2;
    let flagLabelHeight = rowHeight*labelContainerRows
    let flagHeight = flagLabelHeight*1.2;
    return ({
        flagLabel:label,
        flagLabelWidth:labelContainerWidth,
        flagLabelHeight:flagLabelHeight,
        flagWidth:flagWidth,
        flagHeight:flagHeight
    })
}

export default GetFlagDimensions
