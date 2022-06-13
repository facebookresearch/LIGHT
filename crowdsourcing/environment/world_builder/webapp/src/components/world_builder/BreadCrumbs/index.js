/* REACT */
import React from "react";
/* REDUX */
import {useAppDispatch, useAppSelector} from '../../../app/hooks';
import {updateTaskRouterHistory, setTaskRouterCurrentLocation} from '../../../features/taskRouter/taskrouter-slice';
/* STYLES */
import "./styles.css";

import Breadcrumb from 'react-bootstrap/Breadcrumb'

//IconButton -
const BreadCrumbs = ({crumbs}) => {
    /* REDUX DISPATCH FUNCTION */
    const dispatch = useAppDispatch();
    /* ------ REDUX STATE ------ */
    //TASKROUTER
    const currentLocation = useAppSelector((state) => state.taskRouter.currentLocation);
    const taskRouterHistory = useAppSelector((state) => state.taskRouter.taskRouterHistory);
    //HANDLERS
    const crumbClickHandler = (loc, position)=>{
        dispatch(setTaskRouterCurrentLocation(loc));
        let updatedHistory = taskRouterHistory.slice(position);
        dispatch(updateTaskRouterHistory(updatedHistory));
    }
    return (
        <Breadcrumb>
            {
                crumbs.map((crumb, index)=> {
                    const {name, id} = crumb;
                    const formattedCrumb = name.replaceAll("_", " ").toUpperCase()
                    if(index==crumbs.length-1){
                        return(
                            <Breadcrumb.Item className="crumb-active" active key={linkUrl} >
                                {formattedCrumb}
                            </Breadcrumb.Item>
                        )
                    }else{
                    return(
                        <Breadcrumb.Item key={linkUrl} onClick={()=>crumbClickHandler(crumb, index)}>
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
