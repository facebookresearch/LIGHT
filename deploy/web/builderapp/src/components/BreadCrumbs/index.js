/* REACT */
import React from "react";
/* REACT ROUTER */
import { Switch, Route, Link } from 'react-router-dom';
/* STYLES */
import "./styles.css";

import Breadcrumb from 'react-bootstrap/Breadcrumb'

//IconButton - 
const BreadCrumbs = ({crumbs }) => {
  return (
    <Breadcrumb>
        {
            crumbs.map(crumb=> {
                const {name, linkUrl} = crumb;
                return(
                    <Breadcrumb.Item key={linkUrl} as={Link} to={linkUrl}>
                        {name}
                    </Breadcrumb.Item>
                )
            })
        }
    </Breadcrumb>
  );
};

export default BreadCrumbs;