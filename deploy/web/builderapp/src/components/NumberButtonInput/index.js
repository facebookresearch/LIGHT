/* REACT */
import React from 'react';
/* STYLES */
import './styles.css';
/* CUSTOM COMPONENTS */

/* ICONS */
import {AiOutlinePlus} from 'react-icons/ai';
import {AiOutlineMinus} from 'react-icons/ai';

const NumberButtonInput = ({ 
    incrementFunction, 
    decrementFunction, 
    changeFunction, 
    value
})=> {

  return (
    <div className="buttoninput-container">
        <div className="number-button" onClick={decrementFunction}>
            <AiOutlineMinus/>
        </div>
        <input 
            type="number"
            className="number-input"
            value={value ? value : 0}
            onChange={(e)=>{changeFunction(e.target.value)}}

        />
        <div className="number-button" onClick={incrementFunction}>
            <AiOutlinePlus
            
            />
        </div>
    </div>
  );
}

export default NumberButtonInput;