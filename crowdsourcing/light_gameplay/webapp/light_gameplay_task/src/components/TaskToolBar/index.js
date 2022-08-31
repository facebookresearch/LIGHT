
/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React from "react";
/* STYLES */
import "./styles.css"
/* BOOTSTRAP COMPONENTS */
import Navbar from 'react-bootstrap/Navbar'
import Button from 'react-bootstrap/Button'



const TaskToolBar = ({
    activityCounter,
    buttonFunction
})=>{

    return(
        <Navbar bg="dark" variant="dark" fixed="top">
            <div className="tool-container">
                <Navbar.Text>
                    <span className="task-label">GAMEPLAY TASK</span>
                </Navbar.Text>
                <Navbar.Text>
                    <span className="tool-label" >ACTIVITY COUNT:</span>
                        <span className="tool-text" >{activityCounter}</span>
                </Navbar.Text>
                <Button variant="success" onClick={buttonFunction}>Submit</Button>{' '}
            </div>
        </Navbar>
    )
}

export default TaskToolBar;
