/* REACT */
import React from "react";
/* STYLES */
import "./styles.css";
/* BOOTSTRAP COMPONENTS */
//BUTTON
import Button from 'react-bootstrap/Button';

//TextButton -
const TextButton = ({
  clickFunction,
  text,
  disabled
}) => {
  return (
    <Button className="textbutton-container" onClick={clickFunction} variant="primary" disabled={!!disabled}>
      <p style={{ margin: 0, padding: 0 }} className="textbutton-text">
        {text}
      </p>
    </Button>
  );
};

export default TextButton;
