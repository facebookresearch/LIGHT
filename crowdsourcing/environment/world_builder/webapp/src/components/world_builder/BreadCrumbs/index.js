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
    const taskRouterHistory = useAppSelector((state) => state.taskRouter.taskRouterHistory);
    //HANDLERS
    const crumbClickHandler = (loc, position)=>{
        let updatedHistory = taskRouterHistory.slice(0, position);
        console.log("UPDATED BREAD CRUMB HISTORY:  ", updatedHistory)
        dispatch(updateTaskRouterHistory(updatedHistory));
        console.log("CRUMB CLICK LOC:  ", loc)
        dispatch(setTaskRouterCurrentLocation(loc));
    }
    return (
        <Breadcrumb>
            {
                crumbs.map((crumb, index)=> {
                    const {name, id} = crumb;
                    const formattedCrumb = id ? `${name.toUpperCase()}: ${id.replaceAll("_", " ").toUpperCase()}` : `${name.toUpperCase()}` ;
                    if(index==crumbs.length-1){
                        return(
                            <Breadcrumb.Item key={id} className="crumb-active" active >
                                {formattedCrumb}
                            </Breadcrumb.Item>
                        )
                    }else{
                    return(
                        <Breadcrumb.Item key={id} onClick={()=>crumbClickHandler(crumb, index)}>
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
