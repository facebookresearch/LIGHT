import React from "react";
import "./styles.css"
import { BsFillExclamationDiamondFill } from "react-icons/bs";

const ExampleCard =  ({primary, secondary, narration, badReason})=>(
    <div className="card-container">
        <div className="card-row">
            <div className="card-item">
                <p className="card-text"><span className="card-label" style={{color:"gold"}}>PRIMARY:</span>{primary}</p>
            </div>
            <div className="card-item">
                <p className="card-text"><span className="card-label" style={{color:"blue"}}>SECONDARY:</span>{secondary}</p>
            </div>
        </div>
        <div className="card-row">
            <div className="card-item">
                <p className="card-text"><span className="card-label" style={{color:"orange"}}>ACTION:</span>{`USE ${primary} WITH ${secondary}`}</p>
            </div>
        </div>
        <div className="card-row">
            <div className="card-item">
                <p className="card-text"><span className="card-label" style={{color:"green"}}>NARRATION:</span>{narration}</p>
            </div>
        </div>
        {
        badReason ?
        <div className="card-row">
            <div className="card-item">
                <p className="card-text" style={{color:"red"}}><span className="card-label"><BsFillExclamationDiamondFill color="red" /> WHAT'S WRONG? </span> {badReason}</p>
            </div>
        </div>
        :
        null
        }
    </div>
)
export default ExampleCard;
