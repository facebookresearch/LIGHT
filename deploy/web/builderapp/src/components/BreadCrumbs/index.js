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
                    const formattedCrumb = name.replaceAll("_", " ")
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