import React from "react";
import "./styles.css"
import { BsFillExclamationDiamondFill } from "react-icons/bs";

const ExampleCard =  ({primary, primary_desc, secondary, secondary_desc, narration, badReason})=>(
    <div className="card-container">
        <div className="card-row">
            <div className="card-item">
                <p className="card-item__label">
                    <span style={{color:"gold"}}>PRIMARY:</span>
                </p>
                <p className="card-item__text">
                    <span style={{fontWeight:"bold"}}>{primary.toUpperCase()} - </span>{primary_desc}
                </p>
            </div>
        </div>
        <div className="card-row">
            <div className="card-item">
                <p className="card-item__label">
                    <span style={{color:"blue"}}>SECONDARY:</span>
                </p>
                <p className="card-item__text">
                    <span style={{fontWeight:"bold"}}>{secondary.toUpperCase()} - </span>{secondary_desc}
                </p>
            </div>
        </div>
        <div className="card-row">
            <div className="card-item">
                <p className="card-item__label">
                    <span style={{color:"orange"}}>ACTION:</span>
                </p>
                <p className="card-item__text">
                    {`USE ${primary} WITH ${secondary}`}
                </p>
            </div>
        </div>
        <div className="card-row">
            <div className="card-item">
                <p className="card-item__label">
                    <span className="card-label" style={{color:"green"}}>NARRATION:</span>
                </p>
                <p className="card-item__text">
                    {narration}
                </p>
            </div>
        </div>
        {
        badReason ?
        <div className="card-row">
            <div className="card-item__badreasosn">
                <p className="card-label__badreason" style={{color:"red"}}>
                    <span><BsFillExclamationDiamondFill color="red" /> </span> WHAT'S WRONG?
                </p>
                <p className="card-item__text--badreason">
                    {badReason}
                </p>
            </div>
        </div>
        :
        null
        }
    </div>
)
export default ExampleCard;
