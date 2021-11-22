/* REACT */
import React, {useState, useEffect} from "react";
/* STYLES */
import "./styles.css"
/* CUSTOM COMPONENTS */

const TilePath = ({
    tileData,
    alignment
})=>{
    /* ------ LOCAL STATE ------ */
    const [active, setActive] = useState(false);


    /* REACT LIFECYCLE */
    useEffect(()=>{

    } ,[tileData])
    /* HANDLERS */
    const pathClickHandler = ()=>{
        setActive(!active)
    }

    return(
        <div
            onClick={pathClickHandler}
            className={`path-container ${alignment} ${active ?  "active": "" }`}
        />
    )
}
export default TilePath;