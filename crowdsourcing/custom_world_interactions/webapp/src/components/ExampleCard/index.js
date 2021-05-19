import React from "react";

const ExampleCard =  ({primary, secondary, narration, badReason})=>(
    <div className="card-container">
        <div className="card-row">
            <div className="card-item">
                <p><span>PRIMARY:</span>{primary}</p>
            </div>
            <div className="card-item">
                <p><span>SECONDARY:</span>{secondary}</p>
            </div>
        </div>
        <div className="card-row">
            <div className="card-item">
                <p><span>ACTION:</span>{`USE ${primary} WITH ${secondary}`}</p>
            </div>
        </div>
        <div className="card-row">
            <div className="card-item">
                <p><span><i className="bi bi-exclamation-circle" /> WHAT'S WRONG? </span> {badReason}</p>
            </div>
        </div>
    </div>
)
