
/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React, {useEffect, useState} from "react";
/* REDUX */
import { useAppDispatch, useAppSelector } from "../../app/hooks"
/* STYLES */
import "./styles.css"
/* BOOTSTRAP COMPONENTS */
import Navbar from 'react-bootstrap/Navbar'
import Button from 'react-bootstrap/Button'
import Form from 'react-bootstrap/Form'


const TaskToolBar = ({
    buttonFunction,
    toggleFunction,
    toggleValue
})=>{

    return(
        <Navbar bg="dark" variant="dark" fixed="top">
            <div className="tool-container">
                <Navbar.Text>
                    <span className="task-label">GAMEPLAY TASK</span>
                </Navbar.Text>

                    <Button
                        variant= "info"
                        onClick={toggleFunction}
                    >
                        Instructions
                    </Button>

                <Navbar.Text>
                    <span className="tool-label" >World Size: TODO</span>
                </Navbar.Text>
                <Button variant="success" onClick={buttonFunction}>Submit</Button>{' '}
            </div>
        </Navbar>
    )
}

export default TaskToolBar;
