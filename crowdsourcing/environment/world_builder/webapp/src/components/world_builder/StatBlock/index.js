/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React from 'react';
import { useParams } from "react-router-dom";
/* REDUX */
import {useAppDispatch, useAppSelector} from '../../app/hooks';
/* STYLES */
import './styles.css';
/* BOOTSTRAP COMPONENTS */
//LAYOUT
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
//BUTTON
import ButtonGroup from 'react-bootstrap/ButtonGroup'
import Button from 'react-bootstrap/Button'
/* CUSTOM COMPONENTS */

const StatBlock = ({title, fieldNames, data})=> {

  return (
    <div>
        <h1>
            {title}
        </h1>
        {
            fieldNames.map(field =>{

                return(
                    <div className="stat-row">
                        <p className="stat-text">
                            <span className="stat-text label">
                                {field}:{"  "}
                            </span>
                            {data[field] ? data[field] : ""}
                        </p>
                    </div>
                )
            })
        }
    </div>
  );
}

export default StatBlock;
