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



const SuccessBanner = ({
    showSuccess,
    toggleShowSuccess,
    successMessage
})=>{
    return (
        <>
            <Toast show={showSuccess} onClose={toggleShowSuccess} delay={3000} autohide >
            <Toast.Header closeButton={false} style={{backgroundColor:"green", color:"white"}}>
                <BsCheck color="white" style={{fontSize:"18px"}}/>
                <strong className="mr-auto">SUCCESS</strong>
                <BsX color="white" oncClick={toggleShowSuccess} style={{fontSize:"18px"}}/>
            </Toast.Header>
            <Toast.Body>You have successfully completed task</Toast.Body>
            </Toast>
        </>
    )
}
export default SuccessBanner;
