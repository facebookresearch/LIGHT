//REACT
import React from "react";
//STYLING
import "./styles.css"
//CUSTOM COMPONENTS
import TaskButton from "../TaskButton"

//Submission - renders submission button
const Submission = ({
    submitFunction
})=>{
    return(
        <div className="submission-container" >
            <TaskButton
                name="Submit"
                isSelected={false}
                unselectedContainer="submission-button__container"
                unselectedText="submission-selectedbutton__text "
                selectFunction={submitFunction}
            />
        </div>
    )
}
export default Submission;
