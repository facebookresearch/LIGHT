/* REACT */
import React, {useState, useEffect} from 'react';
/* REDUX */
import {useAppDispatch, useAppSelector} from '../../../app/hooks';
/* STYLES */
import './styles.css';
/* BOOTSTRAP COMPONENTS */
//FORM
import ButtonGroup from 'react-bootstrap/ButtonGroup'
import ToggleButton from 'react-bootstrap/ToggleButton'
import Button from 'react-bootstrap/Button'
/* CUSTOM COMPONENTS */


const ButtonToggle = ({
    buttonOptions
})=> {
        const [selectedButtonValue, setSelectedButtonValue] = useState(0);

        return (
          <>
          
            <ButtonGroup>
              {buttonOptions.map((button, id) => {
                const clickFunction = (e)=>{
                  button.clickFunction()
                  setSelectedButtonValue(e.currentTarget.value)
                }
                return (
                  <ToggleButton
                    key={id}
                    active={button.value == selectedButtonValue}
                    id={`radio-${id}`}
                    type="radio"
                    variant={id % 2 ? 'outline-success' : 'outline-danger'}
                    name="toggle"
                    value={button.value}
                    checked={selectedButtonValue === button.value}
                    onChange={clickFunction}
                  >
                    {button.name}
                  </ToggleButton>
                )}
              )}
            </ButtonGroup>
          </>
        );
      }

export default ButtonToggle;