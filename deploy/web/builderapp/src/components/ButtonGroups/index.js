/* REACT */
import React from 'react';
import { useParams, useRouteMatch, useHistory } from "react-router-dom";
/* REDUX */
import {useAppDispatch, useAppSelector} from '../../app/hooks';
/* STYLES */
import './styles.css';
/* BOOTSTRAP COMPONENTS */
//BUTTON
import ButtonGroup from 'react-bootstrap/ButtonGroup'
import Button from 'react-bootstrap/Button'
/* CUSTOM COMPONENTS */
import WorldEditRoutes from "./WorldEditRoutes"


const ButtonGroups = ({buttons, orientation})=> {
  const history = useHistory();

  
  return (
    <ButtonGroup vertical>
        {
            buttons.map(buttonObj => {
                const {name, clickFunction, activeCondition}=buttonObj;
                return(
                    <Button 
                        key={name}
                        variant="outline-secondary" 
                        onClick={clickFunction}
                        active={activeCondition}
                    >
                        {name}
                    </Button>
                )}
            )
        }
    </ButtonGroup>
  );
}

export default ButtonGroups;