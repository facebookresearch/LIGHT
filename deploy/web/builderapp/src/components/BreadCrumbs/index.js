
/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React from "react";
/* REACT ROUTER */
import {  Link } from 'react-router-dom';
/* STYLES */
import "./styles.css";

import Breadcrumb from 'react-bootstrap/Breadcrumb'

//IconButton - 
const BreadCrumbs = ({crumbs }) => {
    return (
        <Breadcrumb>
            {
                crumbs.map((crumb, index)=> {
                    const {name, linkUrl} = crumb;
                    const formattedCrumb = name.replaceAll("_", " ").toUpperCase()
                    if(index==crumbs.length-1){
                        return(
                            <Breadcrumb.Item className="crumb-active" active key={linkUrl} >
                                {formattedCrumb}
                            </Breadcrumb.Item>
                        )
                    }else{
                    return(
                        <Breadcrumb.Item key={linkUrl} linkAs={Link} linkProps= {{to:linkUrl}}>
                            {formattedCrumb}
                        </Breadcrumb.Item>
                    )
                    }
                })
            }
        </Breadcrumb>
    );
};

export default BreadCrumbs;