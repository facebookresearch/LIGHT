/* REACT */
import React, {useEffect, useState} from "react";
/* REDUX */
import { useAppDispatch, useAppSelector } from "../../app/hooks";
import {addMessage} from "../../features/workerActivity/workerActivity-slice";
/* STYLES */
import "./styles.css";
/* CUSTOM COMPONENTS */
import TaskToolBar from "../../components/TaskToolBar";
import RadioForm from "../../components/Forms/RadioForm";
/* BOOTSTRAP COMPONENTS */
import Navbar from 'react-bootstrap/Navbar'
import Modal from 'react-bootstrap/Modal';
import Button from 'react-bootstrap/Button';
/* COPY */
import TaskCopy from "../../TaskCopy";


const OnboardingView = ()=>{
  /* ------ REDUX STATE ------ */
  // VIEW STATE

  /*---------------LOCAL STATE----------------*/

  /* ----REDUX ACTIONS---- */
  // REDUX DISPATCH FUNCTION


  /*---------------HANDLERS----------------*/


  /*---------------LIFECYCLE----------------*/


  return (
    <div className="onboarding-container">
        <Navbar bg="dark" variant="dark">
            <div className="tool-container">
                <Navbar.Text>
                    <span className="task-label">GAMEPLAY TASK ONBOARDING</span>
                </Navbar.Text>
            </div>
        </Navbar>
        <div className="onboarding-body">
            <RadioForm
                questionData={TaskCopy[0]}
            />
        </div>
    </div>
  );
}

export default OnboardingView;
