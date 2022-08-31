
/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React from 'react';
/* STYLES */
import './styles.css';
/* BOOTSTRAP COMPONENTS */
//BUTTON
import ButtonGroup from 'react-bootstrap/ButtonGroup'
import Button from 'react-bootstrap/Button'
/* CUSTOM COMPONENTS */



const ButtonGroups = ({buttons, orientation})=> {

  return (
    <ButtonGroup vertical>
        {
            buttons.map(buttonObj => {
                const {name, clickFunction, activeCondition}=buttonObj;
                return(
                    <Button
                        key={name}
                        variant="outline-secondary"
                        onClick={clickFunction}
                        active={activeCondition}
                    >
                        {name.toUpperCase()}
                    </Button>
                )}
            )
        }
    </ButtonGroup>
  );
}

export default ButtonGroups;
