import React from "react";

function ActionDescription ({ state }) {
    return (
        <div>
            <div className="title is-4">
                <b>ACTION DESCRIPTION</b>
            </div>
            <hr/>
            <p><b>Action:</b> Use {state['primaryObject']} with {state['secondaryObject']}</p>
            <p><i>"{state['actionDescription']}"</i></p> 
        </div>
    );
}

export { ActionDescription };