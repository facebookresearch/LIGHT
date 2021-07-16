//GetFlagDimensions - Function that returns an object  with flag styling dimensions and label based on the length of the label text
const GetFlagDimensions = (
    label, //Flag Text
    width, // ScreenWidth - used to calculate flag width
    rowLength, //Desired number of characters on each row
    rowHeight // Desired heigh of each row
)=>{
    //Default Label Values
    let labelLength = label.length; // Number of characters in label text
    let labelContainerRows=  1 // Default Number of rows
    let labelContainerWidth= width*.9 // default Container width
    if(labelLength>rowLength){
        labelContainerRows=  Math.ceil(labelLength/rowLength);
    }
    let flagWidth = labelContainerWidth+(width*.01)
    let flagHeight = rowHeight*labelContainerRows
    return ({
        flagLabel:label,
        flagLabelWidth:labelContainerWidth,
        flagWidth:flagWidth,
        flagHeight:flagHeight
    })
}

export default GetFlagDimensions
