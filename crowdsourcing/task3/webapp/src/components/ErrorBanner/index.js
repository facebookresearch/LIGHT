//REACT
import React from "react";
//STYLES
import "./styles.css";
//BOOTSTRAP
import Toast from 'react-bootstrap/Toast';
import ToastHeader from 'react-bootstrap/ToastHeader';
import ToastBody from 'react-bootstrap/ToastBody';
//ICONS
import { BsExclamationOctagonFill, BsCheck, BsX } from "react-icons/bs";



const ErrorBanner = ({
    showError,
    toggleShowError,
    errorMessage
})=>{
    return (
        <>
            <Toast show={showError} onClose={toggleShowError} style={{backgroundColor:"red"}} delay={3000} autohide >
            <Toast.Header closeButton={false} style={{backgroundColor:"red", color:"white",textDecoration:"underline", textDecorationColor:"white", display:"flex", justifyContent:"space-between", alignItems:"center", paddingLeft:'2em'}}>
                <span style={{display:"flex", justifyContent:"center", alignItems:"center"}}>
                <BsExclamationOctagonFill color="white" style={{fontSize:"18px"}}/>
                <strong className="mr-auto" style={{color:"white", fontWeight:"bold", marginLeft:"5px"}}>ERROR</strong>
                </span>
                <BsX color="white" onClick={toggleShowError} style={{fontSize:"18px"}} />
            </Toast.Header>
            <Toast.Body style={{fontSize:"18px", color:"white", paddingLeft:'4em'}}>
                <ul>
                {
                errorMessage.map((err, id)=>{
                    if(err.length){
                    return <li key={id}>{err}</li>
                    }
                    })
                }
                </ul>
                </Toast.Body>
            </Toast>
        </>
    )
}
export default ErrorBanner;
