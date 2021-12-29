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
                return(
                    <Breadcrumb.Item key={linkUrl} linkAs={Link} linkProps= {{to:linkUrl}}>
                        {name}
                    </Breadcrumb.Item>
                )
            })
        }
    </Breadcrumb>
  );
};

export default BreadCrumbs;