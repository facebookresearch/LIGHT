import React from "react";

function ActionDescription ({ state }) {
    return (
        <div>
            <div className="title is-4">
                Action Description
            </div>
            <hr/>
            <p><b>Action:</b> Use {state['primaryObject']} with {state['secondaryObject']}</p>
            <p><i>"{state['actionDescription']}"</i></p> 
        </div>
    );
}

export { ActionDescription };